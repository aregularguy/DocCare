# DentNest Backup & Restore Guide

## How Backup Works

The backup is a **full copy** of `dentnest.db` — the single file that holds all your data:

| Data | Table |
|------|-------|
| Patients | `patients` |
| Treatments | `treatments` |
| Payments / Billing | `payments` |
| Due Amounts | Calculated from `treatments.total_cost - sum(payments)` |
| Prescriptions | `prescriptions` |
| Medicines | `medicines` |
| Treatment Types | `treatment_types` |

---

## Transferring Data Between Machines

### Option 1: Restore Backup (Recommended)

Use this when moving to a new machine or replacing all data on the target machine.

**On the source machine (e.g. Ubuntu):**

1. Open DentNest → Settings → Database Backup
2. Click **Backup Now** → choose a folder (USB drive, Google Drive, etc.)
3. A `.db` file is saved with a timestamp (e.g. `dentnest_backup_20250501_143000.db`)

**On the target machine (e.g. Windows):**

1. Open DentNest → Settings → Database Backup
2. Click **Restore Backup** → select the `.db` file
3. Review the record count preview → click **Yes** to confirm
4. Done — all pages refresh with the restored data

> A safety backup of the current database is automatically created before restoring.

### Option 2: Import & Merge

Use this when **both machines have unique data** and you want to combine them.

**Example:** Ubuntu has patients A, B, C. Windows has patients B, C, D.
After merge, Windows will have A, B, C, D. Patient B and C are not duplicated.

1. Backup from the source machine (same steps as Option 1)
2. On the target machine, click **Import & Merge** → select the `.db` file
3. Review the preview → click **Yes**
4. A summary shows how many new records were imported

**How duplicates are detected:**

| Table | Matched by |
|-------|-----------|
| Patients | name + mobile number |
| Treatment Types | name |
| Medicines | name |
| Treatments | patient + type + start date + cost |
| Payments | treatment + amount + date |
| Prescriptions | treatment + medicine + date + session |

> Only new records are added. Existing records are never modified or deleted.

### Option 3: Manual File Copy (No App Features Needed)

Use this if the target machine has an older version without Restore/Merge buttons.

1. **Close DentNest on both machines**
2. On the source machine, copy `data/dentnest.db`
3. On the target machine:
   - Replace `data/dentnest.db` with the copied file
   - **Delete** `data/dentnest.db-wal` and `data/dentnest.db-shm` if they exist
4. Open DentNest

> Closing the app before copying is critical — it flushes recent writes into the `.db` file.

---

## Important: WAL Files

DentNest uses SQLite WAL (Write-Ahead Logging) mode. This creates two sidecar files:

- `dentnest.db-wal` — recent writes not yet merged into the main file
- `dentnest.db-shm` — shared memory index

**Why this matters:**

- If you copy only `dentnest.db` while the app is running, recent data may be missing
- If you paste a new `.db` file but leave old `-wal`/`-shm` files, the old data comes back

**The app now handles this automatically:**

- WAL is flushed into the main `.db` after every small write (`wal_autocheckpoint = 10`)
- WAL is flushed before every backup operation
- Restore deletes stale `-wal`/`-shm` files after replacing the `.db`

---

## Safety Features

- **Auto-backup on startup** — saved in `data/backups/` (last 7 kept)
- **Safety backup before restore/merge** — so you can undo if something goes wrong
- **Validation** — the app checks that the selected file is a valid DentNest database before restoring or merging
- **Record preview** — shows how many patients, treatments, etc. are in the file before you confirm
