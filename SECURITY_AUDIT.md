# DentNest Security Audit Report

> Auditor: Claude Code (Opus 4.6) — Adversarial Security Review
> Date: 2026-04-22
> Scope: Full codebase, all layers, attacker-perspective

---

## Threat Model

### Attacker Types

| Attacker | Access Level | Goal |
|----------|-------------|------|
| **Malware on clinic PC** | File system read access | Steal patient data from SQLite file |
| **Disgruntled staff** | Physical access to running app | Delete/modify patient records, steal data |
| **Stolen laptop** | Full disk access | Extract all patient PII and medical history |
| **Competing clinic** | Obtains database backup | Business intelligence, patient poaching |
| **Patient themselves** | Sees screen during visit | Access other patients' records via open app |

### Sensitive Assets

| Asset | Location | Protection |
|-------|----------|------------|
| Patient names, phone numbers, addresses | `data/dentnest.db` (patients table) | **NONE — plain text** |
| Medical history (treatments, prescriptions) | `data/dentnest.db` (treatments, prescriptions tables) | **NONE — plain text** |
| Financial records (payments, costs) | `data/dentnest.db` (payments table) | **NONE — plain text** |
| Doctor/clinic settings (name, reg number) | `data/settings.json` | **NONE — plain text** |
| Prescription PDFs | Generated at print time | Exists in print spooler/temp files |

### Trust Boundaries

```
[No boundary] → App runs with full access to everything
                 No login, no roles, no permissions
                 Anyone who opens the .exe IS the admin
```

### Entry Points

| Entry Point | What attacker controls |
|-------------|----------------------|
| All UI text fields | Patient name, mobile, address, notes, amounts |
| File system | Direct SQLite file access, settings.json |
| Database file | Can be copied, opened with any SQLite browser |
| Process memory | Can be dumped — contains decrypted data |

---

## Vulnerability Findings

---

### CRITICAL-1: No Authentication — Anyone Can Access Everything

**Severity:** CRITICAL
**Affected:** Entire application
**Files:** All services, all UI widgets

**Description:**
There is zero authentication. No login screen, no password, no user accounts, no roles. Whoever opens the app has full unrestricted access to every patient record, every payment, every prescription. There is no way to know who accessed or modified data.

**Exploitation:**
1. Open the app
2. You can now: view all patients, delete any patient, modify any payment, print any prescription, export any data

**Impact:**
- Any clinic staff can access all records
- No accountability for who did what
- Violates IT Rules 2011 requirement for access control on SPDI
- No audit trail for regulatory compliance

**Recommended Fix:**
- Add login screen with password
- Add role-based access (doctor, receptionist, read-only)
- Log every action with username and timestamp

---

### CRITICAL-2: Unencrypted Patient Data on Disk

**Severity:** CRITICAL
**Affected:** `src/database/db_manager.py` line 47-51
**File:** `data/dentnest.db`

**Description:**
The SQLite database is stored as a plain, unencrypted file. Anyone who copies this file can open it with any SQLite browser and read every patient's name, phone number, address, medical treatments, prescriptions, and payment history.

**Exploitation:**
```bash
# Copy the database
cp /path/to/DentNest/data/dentnest.db /tmp/stolen.db

# Open with any SQLite tool
sqlite3 /tmp/stolen.db "SELECT name, mobile_number, city FROM patients"
# Output: Full patient directory with phone numbers
```

**Impact:**
- Complete exposure of all patient PII
- Complete exposure of all medical records
- Laptop theft = full data breach
- Malware can silently copy the 1 file
- Violates IT Rules 2011 (SPDI requires reasonable security for medical records)
- Potential liability up to Rs. 250 crore under DPDPA 2023

**Recommended Fix:**
- Use SQLCipher for full database encryption, OR
- Field-level encryption for sensitive columns (name, mobile, address)
- Derive encryption key from login password

---

### CRITICAL-3: No Object-Level Access Control (IDOR)

**Severity:** CRITICAL
**Affected:** All repositories and services
**Key files:**
- `src/repositories/patient_repository.py` — all methods
- `src/services/treatment_service.py` — `create_treatment()`, `get_patient_treatments()`
- `src/services/payment_service.py` — `add_payment()`, `delete_payment()`

**Description:**
Every data access method accepts an integer ID and returns the data. There is no check that the caller should have access to that record. In a multi-user scenario (receptionist vs doctor), any user could access any patient's data by guessing or iterating IDs.

**Exploitation:**
```python
# Iterate through all patient IDs to dump entire database
for patient_id in range(1, 10000):
    patient = patient_service.get_patient(patient_id)
    if patient:
        treatments = treatment_service.get_patient_treatments(patient_id)
        # Full medical + financial history extracted
```

**Impact:** Complete data exfiltration with no authentication required

**Recommended Fix:**
- Implement session-based user context
- Every query should filter by authorized scope
- Log all data access events

---

### HIGH-1: TOCTOU Race Condition in Payment Processing

**Severity:** HIGH
**Affected:** `src/services/payment_service.py` lines 21-67

**Description:**
Payment validation and payment creation are not atomic. The code:
1. Reads `pending_amount` (Query 1)
2. Validates that payment <= pending (Python check)
3. Creates payment record (Query 2)
4. Increments `amount_paid` (Query 3)

Between steps 1 and 4, another payment could be processed for the same treatment.

**Exploitation:**
```
Timeline:
T1: Request A reads pending_amount = Rs.5000
T2: Request B reads pending_amount = Rs.5000 (still old value)
T3: Request A validates Rs.5000 payment — passes
T4: Request B validates Rs.5000 payment — passes (stale check)
T5: Request A creates payment + increments → amount_paid = 5000
T6: Request B creates payment + increments → amount_paid = 10000
Result: Rs.10000 paid for Rs.5000 treatment
```

**Impact:** Financial data corruption, overpayment

**Recommended Fix:**
- Wrap the entire add_payment operation in a database transaction
- Use `SELECT ... FOR UPDATE` pattern or check-and-set at DB level
- Add CHECK constraint: `amount_paid <= total_cost`

---

### HIGH-2: SQL Injection in LIMIT Clauses

**Severity:** HIGH
**Affected:** `src/repositories/patient_repository.py` line 54-57

**Description:**
```python
def get_recent_patients(self, limit: int = 10) -> List[Patient]:
    query = f"""
        SELECT * FROM patients
        ORDER BY updated_at DESC
        LIMIT {limit}
    """
```

The `limit` parameter is inserted via f-string, not parameterized. While the `payment_repository.py` LIMIT was fixed (bug #17), this one in `patient_repository.py` was missed.

**Exploitation:**
If `limit` is ever sourced from user input:
```python
get_recent_patients(limit="1 UNION SELECT sql,2,3,4,5,6,7,8 FROM sqlite_master--")
# Leaks entire database schema
```

**Impact:** Database schema disclosure, potential data extraction

**Recommended Fix:**
```python
query = "SELECT * FROM patients ORDER BY updated_at DESC LIMIT ?"
rows = self.db.fetch_all(query, (int(limit),))
```

---

### HIGH-3: No Database Integrity Constraints

**Severity:** HIGH
**Affected:** `src/database/migrations.py` lines 15-78

**Description:**
The database schema is missing critical constraints:

```sql
-- Mobile number is NOT UNIQUE
mobile_number TEXT NOT NULL,  -- allows duplicates

-- No CHECK constraint on amounts
total_cost REAL DEFAULT 0,    -- allows negative values
amount_paid REAL DEFAULT 0,   -- allows negative values

-- No CHECK constraint on age
age INTEGER NOT NULL,          -- allows 0, -1, 999999
```

**Exploitation:**
Direct SQL access can insert:
- Negative payment amounts (fraudulent refunds)
- Duplicate patient records (same phone number)
- Impossible ages (age = -5 or age = 9999)
- Negative treatment costs

**Impact:** Data integrity violations, financial fraud

**Recommended Fix:**
```sql
mobile_number TEXT NOT NULL UNIQUE,
age INTEGER NOT NULL CHECK(age > 0 AND age <= 150),
total_cost REAL DEFAULT 0 CHECK(total_cost >= 0),
amount_paid REAL DEFAULT 0 CHECK(amount_paid >= 0 AND amount_paid <= total_cost),
```

---

### HIGH-4: Sensitive Data in Logs

**Severity:** HIGH
**Affected:** `src/database/db_manager.py` lines 128-130, 146-148

**Description:**
```python
logger.error(f"fetch_one failed: {e} | query: {query}")
```

Failed SQL queries are logged with full query text. If the query contains patient names, phone numbers, or other PII in WHERE clauses, these end up in log files.

**Impact:** PII leakage through log files

**Recommended Fix:**
- Log query template only, not parameter values
- Or redact sensitive parameters before logging

---

### MEDIUM-1: Unbounded Search Returns All Patients

**Severity:** MEDIUM
**Affected:** `src/repositories/patient_repository.py` lines 14-30

**Description:**
```python
def search(self, query: str) -> List[Patient]:
    search_pattern = f"%{query}%"
    sql = """SELECT * FROM patients
        WHERE name LIKE ? OR mobile_number LIKE ? OR city LIKE ?
        ORDER BY name"""
```

Empty string search (`""`) becomes `%%` which matches ALL rows. No LIMIT clause. A clinic with 50,000+ patient records over years could have the entire table loaded into memory.

**Impact:** App freeze / out-of-memory crash (denial of service)

**Recommended Fix:**
- Add `LIMIT 100` to search queries
- Reject empty search strings
- Add pagination

---

### MEDIUM-2: No Patient ID Validation in Treatment Creation

**Severity:** MEDIUM
**Affected:** `src/services/treatment_service.py` lines 17-60

**Description:**
`create_treatment()` verifies `treatment_type_id` exists but does NOT verify `patient_id` exists. SQLite foreign key constraints should catch this, but only if `PRAGMA foreign_keys = ON` is set before the connection is fully initialized.

**Impact:** Orphaned treatment records, data integrity issues

**Recommended Fix:**
- Verify patient exists in service layer before creating treatment
- Ensure foreign key constraints are enforced at DB level

---

### MEDIUM-3: Settings Value Injection

**Severity:** MEDIUM
**Affected:** `src/services/settings_service.py` lines 44-60

**Description:**
Settings values are not length-limited or type-validated. An attacker with file system access could modify `settings.json` to contain extremely large values.

```json
{"doctor_name": "<10MB string here>"}
```

This gets loaded into memory and rendered in the prescription PDF HTML template, potentially crashing the app.

**Impact:** Denial of service, memory exhaustion

**Recommended Fix:**
- Validate value types and lengths when reading settings
- Set maximum string lengths (e.g., 500 chars for names)

---

### LOW-1: Database File Permissions Not Set

**Severity:** LOW
**Affected:** `src/database/db_manager.py` line 40-42

**Description:**
```python
db_dir.mkdir(exist_ok=True)
# No chmod / permission setting
```

The `data/` directory and `dentnest.db` file are created with default OS permissions. On a shared computer, other user accounts may be able to read the database.

**Recommended Fix:**
- Set restrictive permissions: `os.chmod(db_path, 0o600)` (owner read/write only)

---

### LOW-2: No Log File Rotation

**Severity:** LOW
**Affected:** `src/main.py` lines 12-20

**Description:**
Logs go to stdout only. If redirected to a file, they grow unbounded. Long-running clinic use could fill disk.

**Recommended Fix:**
- Use `RotatingFileHandler` with max size

---

### LOW-3: PyInstaller Spec Not Pinned

**Severity:** LOW
**Affected:** `DentNest.spec`, `requirements.txt`

**Description:**
Dependencies use `>=` minimum versions. A `pip install` could pull in a compromised newer version (supply chain attack, like the litellm incident you saw).

**Recommended Fix:**
- Pin exact versions: `PyQt6==6.6.1`
- Use `pip install --require-hashes`

---

## Attack Chains

### Chain 1: Complete Data Breach (Stolen Laptop)
```
Laptop stolen from clinic
    → Open data/dentnest.db with DB Browser for SQLite
    → Export all patients, treatments, payments, prescriptions
    → All patient PII + medical records exposed
    → Doctor faces liability under DPDPA 2023
```
**Blocked by:** Database encryption (SQLCipher or field-level)

### Chain 2: Insider Data Theft (Disgruntled Receptionist)
```
Receptionist opens app (no login needed)
    → Views all patient records (no access control)
    → Copies patient phone numbers + treatment history
    → Sells to competing clinic or insurance company
    → No audit log = doctor can't prove who leaked
```
**Blocked by:** Authentication + role-based access + audit logging

### Chain 3: Financial Manipulation
```
Staff member opens app
    → Creates fake patient record
    → Adds treatment with inflated cost
    → Records payment as "cash" (no verification)
    → Pockets the cash, records show patient paid
    → No audit trail = undetectable
```
**Blocked by:** Authentication + audit log + payment verification workflow

### Chain 4: Denial of Service via Data Corruption
```
Attacker gets temporary access to PC
    → Opens data/dentnest.db directly
    → Runs: DELETE FROM patients;
    → All patient records permanently deleted
    → No backup exists = total data loss
    → Clinic operations halt
```
**Blocked by:** Database encryption + file permissions + backup system

### Chain 5: Race Condition Payment Fraud
```
Attacker (or bug) triggers concurrent payment submissions
    → Two Rs.5000 payments processed for Rs.5000 treatment
    → amount_paid becomes Rs.10000 (double the treatment cost)
    → Financial records now inconsistent
    → Cascading errors in analytics and reporting
```
**Blocked by:** Database transaction isolation + CHECK constraints

---

## Secure Design Improvements (Priority Order)

### 1. Authentication Layer (Blocks Chains 1, 2, 3)
- Login screen with password hash (bcrypt/argon2)
- Session timeout after 15 minutes idle
- Role-based access: Doctor (full), Receptionist (limited), Viewer (read-only)

### 2. Database Encryption (Blocks Chains 1, 4)
- SQLCipher for full-database AES-256 encryption, OR
- Field-level encryption for PII columns
- Derive key from login password

### 3. Audit Logging (Blocks Chains 2, 3)
- Log every: patient view, create, edit, delete
- Log every: payment add, delete
- Log every: prescription print
- Include: timestamp, user, action, record ID
- Store in separate audit table (append-only)

### 4. Database Constraints (Blocks Chain 5)
```sql
ALTER TABLE patients ADD CONSTRAINT unique_mobile UNIQUE(mobile_number);
ALTER TABLE treatments ADD CHECK(total_cost >= 0);
ALTER TABLE treatments ADD CHECK(amount_paid >= 0);
ALTER TABLE treatments ADD CHECK(amount_paid <= total_cost);
ALTER TABLE payments ADD CHECK(amount > 0);
```

### 5. Automated Backup (Blocks Chain 4)
- Daily SQLite backup to timestamped file
- Keep last 30 days
- Optional: encrypted backup to USB/cloud

### 6. Input Bounds
- Max 100 chars for patient name
- Max 500 chars for address/notes
- Max Rs.99,99,999 for treatment cost
- Search results limited to 100 rows

---

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 3 | Open — require architectural changes |
| High | 4 | Open — require code + schema changes |
| Medium | 3 | Open |
| Low | 3 | Open |
| **Total** | **13** | |

**The #1 risk:** An unencrypted database with no authentication on a machine that handles sensitive medical data. This is both a security vulnerability and a legal liability under Indian law (IT Rules 2011, DPDPA 2023).
