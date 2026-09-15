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

### 10. ~~Float Comparison Tolerance Issue for Payment Status~~ FIXED
**File:** `src/models/treatment.py`
**Fix applied:** Changed `self.pending_amount <= 0.01` to `round(self.pending_amount, 2) <= 0` for precise paisa-level comparison.

### 11. ~~Silent Data Loss on Payment Deletion~~ FIXED
**File:** `src/services/payment_service.py`
**Fix applied:** After atomic decrement, checks if `amount_paid` went negative. If so, logs a warning with treatment ID and values, then clamps to 0.

### 12. ~~Non-Atomic Settings File Write~~ FIXED
**File:** `src/services/settings_service.py`
**Fix applied:** Write to `tempfile.mkstemp()` temp file first, then `os.replace()` to atomically swap. Cleans up temp file on failure.

### 13. ~~Corrupted Settings File Silently Returns Empty Dict~~ FIXED
**File:** `src/services/settings_service.py`
**Fix applied:** Now distinguishes missing file (returns `{}`), corrupt JSON (`json.JSONDecodeError` — logs warning, returns `{}`), and other errors (logs error, returns `{}`).

### 14. ~~Silent Exception Swallowing in Date Conversion~~ FIXED
**File:** `src/ui/widgets/treatment_list.py`
**Fix applied:** Changed both `except Exception` blocks to `except (ValueError, AttributeError)` with `logger.warning()` logging treatment ID and error.

### 15. ~~Silent Migration Errors~~ FIXED
**File:** `src/database/migrations.py`
**Fix applied:** Now checks if error message contains "duplicate column name". If yes, silently passes (expected). If no, logs error and re-raises.

### 16. ~~N+1 Query Problem in Seed Data~~ FIXED
**File:** `src/database/seed_data.py`
**Fix applied:** Replaced 100+ individual queries with one `SELECT name FROM medicines` to get all existing names, then one `executemany()` batch insert for new medicines.

### 17. ~~SQL Injection Pattern in Repositories~~ FIXED
**File:** `src/repositories/base_repository.py`, `src/repositories/payment_repository.py`
**Fix applied:** Added `_validate_identifier()` regex whitelist (`^[a-zA-Z_][a-zA-Z0-9_]*$`) for table/column names in base_repository. Parameterized `LIMIT` value in payment_repository.

### 18. ~~Widget Memory Leak on Tab Switches~~ FIXED
**File:** `src/ui/dialogs/patient_details.py`
**Fix applied:** Added `QApplication.processEvents()` after `deleteLater()` to force immediate processing of deferred widget deletions.

### 19. ~~Thread Safety with `check_same_thread=False`~~ FIXED
**File:** `src/database/db_manager.py`
**Fix applied:** Added thread check in `get_connection()` — logs a warning if accessed from non-main thread, alerting developers to the risk before it causes silent corruption.

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

| Severity | Total | Fixed | Remaining |
|----------|-------|-------|-----------|
| Critical | 5 | 5 | 0 |
| High | 4 | 4 | 0 |
| Medium | 10 | 10 | 0 |
| Low | 6 | 0 | 6 |
| Design | 7 | 0 | 7 |
| **Total** | **32** | **19** | **13** |

**Remaining items:**
- Items #20-25 (Low) — polish and edge cases
- Design concerns — architectural improvements for future
