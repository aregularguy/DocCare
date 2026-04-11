# DentNest Code Review - Bugs, Edge Cases & Missing Error Handling

> Reviewed by: Claude Code (Opus 4.6)
> Date: 2026-04-10
> Scope: Full codebase audit for crashes, data corruption, edge cases, and missing error handling

---

## Critical (Fix Immediately)

### 1. ~~Race Condition in Payment Addition — Can Double-Count Payments~~ FIXED
**File:** `src/services/payment_service.py`, `src/repositories/treatment_repository.py`
**Fix applied:** Added `increment_amount_paid()` method that uses atomic SQL `UPDATE treatments SET amount_paid = amount_paid + ? WHERE id = ?`. Both `add_payment` and `delete_payment` now use this instead of read-then-write.

### 2. ~~Possible TypeError in Payment List — QDate Methods Called Wrong~~ VERIFIED OK
**File:** `src/ui/widgets/payment_list.py` ~Line 271
**Status:** On closer inspection, `self.date_edit.date()` always returns `QDate`, and `QDate.year()` etc. are methods that return `int`. The `date(q_date.year(), q_date.month(), q_date.day())` pattern is correct. No fix needed — false alarm.

### 3. ~~Possible AttributeError — `p.mobile` vs `p.mobile_number`~~ FIXED
**File:** `src/ui/widgets/payment_list.py` ~Line 210
**Fix applied:** Changed `p.mobile` to `p.mobile_number` to match the Patient model field name.

### 4. ~~No Transaction Rollback on Database Errors~~ FIXED
**File:** `src/database/db_manager.py`
**Fix applied:** Wrapped `execute()` and `executemany()` in try/except with `conn.rollback()` on failure, then re-raise.

### 5. ~~IndexError — Unsafe `meds[0]` Access in Patient Details~~ FIXED
**File:** `src/ui/dialogs/patient_details.py` ~Line 296
**Fix applied:** Changed `if meds[0].prescribed_date:` to `if meds and meds[0].prescribed_date:`

---

## High Severity

### 6. ~~HTML Injection in Prescription PDF~~ FIXED
**File:** `src/ui/dialogs/patient_details.py`
**Fix applied:** Added `import html as html_mod` and wrapped patient name, age, mobile, and medicine names with `html_mod.escape()` in the prescription HTML template.

### 7. ~~Unprotected Data Fetch on PatientDetails Init~~ FIXED
**File:** `src/ui/dialogs/patient_details.py` ~Lines 51-54
**Fix applied:** Added null guard — if `patient` or `patient.id` is None, sets treatments/totals to empty/zero instead of crashing.

### 8. ~~No Error Handling in Fetch Methods~~ FIXED
**File:** `src/database/db_manager.py`
**Fix applied:** Wrapped `fetch_one()` and `fetch_all()` in try/except with `logger.error()` logging the failed query, then re-raise.

### 9. ~~Timer-Based Navigation Can Crash After Widget Deletion~~ FIXED
**File:** `src/ui/widgets/patient_list.py`
**Fix applied:** Replaced direct `self.on_cancel` callback with a `_safe_cancel` wrapper that catches `RuntimeError` (deleted widget) gracefully.

---

## Medium Severity

### 10. Float Comparison Tolerance Issue for Payment Status
**File:** `src/models/treatment.py` ~Line 71
**Issue:** `self.pending_amount <= 0.01` uses a hardcoded tolerance. For large bills, 0.01 is fine. But for micro-amounts or bulk operations, this could incorrectly mark treatments as fully paid when they still have pending balance.
```python
# Current:
return self.pending_amount <= 0.01

# Better: Use exact comparison after rounding
return round(self.pending_amount, 2) <= 0
```

### 11. Silent Data Loss on Payment Deletion
**File:** `src/services/payment_service.py` ~Line 138
**Issue:** `max(0, treatment.amount_paid - payment.amount)` silently truncates to 0 if data is already inconsistent (payment amount > recorded amount_paid). This hides data corruption instead of flagging it.
```python
# Fix: Log a warning when data inconsistency detected
new_paid = treatment.amount_paid - payment.amount
if new_paid < 0:
    logger.warning(f"Data inconsistency: treatment {treatment.id} amount_paid "
                   f"({treatment.amount_paid}) < payment ({payment.amount})")
    new_paid = 0
```

### 12. Non-Atomic Settings File Write
**File:** `src/services/settings_service.py` ~Lines 66-68
**Issue:** Writes directly to the settings file. If the app crashes during write, the settings file is corrupted and unreadable on next startup.
```python
# Fix: Write to temp file, then rename (atomic on most OS)
import tempfile
tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(_SETTINGS_PATH))
with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, _SETTINGS_PATH)
```

### 13. Corrupted Settings File Silently Returns Empty Dict
**File:** `src/services/settings_service.py` ~Line 62
**Issue:** `except Exception: return {}` swallows all errors. A corrupted JSON file is treated the same as a missing file — no way to know settings were lost.

### 14. Silent Exception Swallowing in Date Conversion
**File:** `src/ui/widgets/treatment_list.py` ~Lines 707-713
**Issue:** Generic `except Exception` hides real errors in date parsing. Bad dates silently fall through to a string representation.
```python
# Fix: Catch specific exceptions and log
except (ValueError, AttributeError) as e:
    logger.warning(f"Date parse error for treatment {treatment.id}: {e}")
    date_str = str(treatment.start_date) if treatment.start_date else "N/A"
```

### 15. Silent Migration Errors
**File:** `src/database/migrations.py` ~Lines 88-92
**Issue:** `ALTER TABLE` migrations use `except Exception: pass`. Real errors (disk full, permissions, corruption) are silently ignored — schema changes might not apply.
```python
# Fix: Only catch the specific "column already exists" error
except sqlite3.OperationalError as e:
    if "duplicate column name" not in str(e).lower():
        raise
```

### 16. N+1 Query Problem in Seed Data
**File:** `src/database/seed_data.py` ~Lines 120-129
**Issue:** Loops through 50+ medicines with individual SELECT + INSERT per item. Should batch check and insert.

### 17. SQL Injection Pattern in Repositories
**File:** `src/repositories/base_repository.py` ~Line 35, `payment_repository.py` ~Line 119
**Issue:** Dynamic table/column names and LIMIT values use f-strings instead of parameterized queries. While currently fed from internal code (not user input), this pattern is dangerous if the code evolves.
```python
# Current:
query = f"SELECT * FROM payments LIMIT {limit}"

# Fix: Parameterize
query = "SELECT * FROM payments LIMIT ?"
db.fetch_all(query, (limit,))
```

### 18. Widget Memory Leak on Tab Switches
**File:** `src/ui/dialogs/patient_details.py` ~Lines 198-199
**Issue:** `old_widget.deleteLater()` is called on tab switch, but rapid switching can queue up multiple deletions. Qt's deferred deletion might not keep up, leading to gradual memory growth during long sessions.

### 19. Thread Safety with `check_same_thread=False`
**File:** `src/database/db_manager.py` ~Line 49
**Issue:** SQLite connection allows multi-thread access. While WAL mode helps, concurrent writes from different threads can still cause `database is locked` errors. App currently appears single-threaded, but any future background tasks will break.

---

## Low Severity

### 20. Whitespace-Only Address Accepted
**File:** `src/services/patient_service.py` ~Line 64
**Issue:** `address.strip() if address else None` doesn't reject whitespace-only strings. `"   "` becomes `""` which is truthy and gets saved.

### 21. Hardcoded 10-Digit Mobile Validation
**File:** `src/utils/validators.py` ~Line 26
**Issue:** Only accepts exactly 10 digits (India-specific). Not flexible for international numbers or numbers with country codes.

### 22. Treatment Type Name Empty String Not Caught
**File:** `src/ui/widgets/treatment_list.py` ~Line 688
**Issue:** `treatment.treatment_type_name or "N/A"` handles None but not empty string `""` (which is falsy in Python, so this is actually fine). Verify if the database can store empty strings for type names.

### 23. No Database File Permission Check on Startup
**File:** `src/main.py`
**Issue:** App doesn't verify the `data/` directory exists and is writable before trying to create/open the database. On restricted file systems or when run from read-only media, will crash with an unclear error.

### 24. No Disk Space Check Before Database Operations
**Issue:** No global handling for `sqlite3.OperationalError: database or disk is full`. Long-running clinic use could fill disk without warning.

### 25. Missing `__init__.py` Verification
**Issue:** If any `__init__.py` file is accidentally deleted, the entire module import chain breaks with confusing errors.

---

## Design Concerns (Not Bugs, But Worth Noting)

| Concern | Location | Notes |
|---------|----------|-------|
| No database backup mechanism | Global | Single SQLite file — if corrupted, all data is lost |
| No data export feature | Global | Doctor can't export patient data to CSV/Excel |
| No audit log | Global | No record of who changed what and when |
| No database connection pooling | db_manager.py | Single connection reused — fine for single-user |
| Hardcoded font families | styles.py | Fonts may not be available on all Windows machines |
| No graceful shutdown | main.py | No cleanup of database connections on app close |
| Recursive guard pattern | patient_details.py | `_refreshing_overview` flag is fragile — consider proper state machine |

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 5 |
| High | 4 |
| Medium | 10 |
| Low | 6 |
| Design | 7 |
| **Total** | **32** |

**Priority order for fixes:**
1. Items #1-5 (Critical) — can cause crashes or data corruption
2. Items #6-9 (High) — can cause crashes in specific scenarios
3. Items #10-19 (Medium) — data integrity and robustness
4. Items #20-25 (Low) — polish and edge cases
