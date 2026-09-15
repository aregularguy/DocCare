"""Database backup service — manual, auto-backup, restore, and smart merge."""
import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

import sys as _sys
if getattr(_sys, 'frozen', False):
    _DATA_DIR = os.path.join(os.path.dirname(_sys.executable), "data")
else:
    _DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data"
    )

_DB_PATH       = os.path.join(_DATA_DIR, "dentnest.db")
_AUTO_BACKUP_DIR = os.path.join(_DATA_DIR, "backups")
_MAX_AUTO_BACKUPS = 7   # keep last 7 auto-backups (one per day)

logger = logging.getLogger(__name__)


_REQUIRED_TABLES = {"patients", "treatment_types", "medicines",
                     "treatments", "payments", "prescriptions"}


class BackupService:
    """Handles database backup operations."""

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _checkpoint_wal():
        """Flush WAL into the main DB file so a file-copy is complete."""
        try:
            from ..database.db_manager import DatabaseManager
            conn = DatabaseManager().get_connection()
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            logger.info("WAL checkpoint completed before backup/copy")
        except Exception as e:
            logger.warning(f"WAL checkpoint failed (non-critical): {e}")

    @staticmethod
    def _validate_dentnest_db(db_path: str) -> tuple[bool, str]:
        """Check that db_path is a valid DentNest database.

        Returns (is_valid, message).
        """
        if not os.path.isfile(db_path):
            return False, "File does not exist."
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            return False, f"Cannot open as SQLite database: {e}"

        missing = _REQUIRED_TABLES - tables
        if missing:
            return False, (
                f"Not a valid DentNest database.\n"
                f"Missing tables: {', '.join(sorted(missing))}"
            )
        return True, "Valid DentNest database."

    @staticmethod
    def _get_record_counts(db_path: str) -> dict[str, int]:
        """Return {table_name: row_count} for every required table."""
        counts: dict[str, int] = {}
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            for t in sorted(_REQUIRED_TABLES):
                row = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()
                counts[t] = row[0] if row else 0
            conn.close()
        except Exception:
            pass
        return counts

    # ── public API ────────────────────────────────────────────────────────

    def backup_now(self, destination_folder: str) -> tuple[bool, str]:
        """Copy the DB to destination_folder with a timestamp filename.

        Returns (success, message/path).
        """
        if not os.path.exists(_DB_PATH):
            return False, "Database file not found. Nothing to backup."

        try:
            self._checkpoint_wal()
            os.makedirs(destination_folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = os.path.join(destination_folder, f"dentnest_backup_{timestamp}.db")
            shutil.copy2(_DB_PATH, dest_file)
            logger.info(f"Manual backup created: {dest_file}")
            return True, dest_file
        except PermissionError:
            return False, "Permission denied. Choose a different folder."
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False, f"Backup failed: {e}"

    def auto_backup(self) -> tuple[bool, str]:
        """Create an automatic backup in data/backups/ — called on app startup.

        Keeps only the last _MAX_AUTO_BACKUPS backups.
        Returns (success, message).
        """
        if not os.path.exists(_DB_PATH):
            return False, "No database to backup."

        try:
            self._checkpoint_wal()
            os.makedirs(_AUTO_BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = os.path.join(_AUTO_BACKUP_DIR, f"auto_{timestamp}.db")
            shutil.copy2(_DB_PATH, dest_file)
            logger.info(f"Auto-backup created: {dest_file}")

            self._prune_old_backups()
            return True, dest_file
        except Exception as e:
            logger.warning(f"Auto-backup failed (non-critical): {e}")
            return False, str(e)

    def get_last_backup_info(self) -> dict:
        """Return info about the most recent backup (auto or manual)."""
        candidates = []

        # Check auto-backup folder
        if os.path.isdir(_AUTO_BACKUP_DIR):
            for f in Path(_AUTO_BACKUP_DIR).glob("*.db"):
                candidates.append(f)

        if not candidates:
            return {"exists": False, "path": "", "time": ""}

        latest = max(candidates, key=lambda p: p.stat().st_mtime)
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        return {
            "exists": True,
            "path": str(latest),
            "time": mtime.strftime("%d %b %Y, %I:%M %p"),
        }

    def get_db_size(self) -> str:
        """Return DB file size as a human-readable string."""
        try:
            size = os.path.getsize(_DB_PATH)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.2f} MB"
        except Exception:
            return "Unknown"

    def cloud_backup(self) -> tuple[bool, str]:
        """Backup to the user-configured cloud-synced folder (if set).

        Returns (success, message/path).
        """
        from .settings_service import SettingsService
        folder = SettingsService().get("cloud_backup_folder")
        if not folder:
            return False, "No cloud backup folder configured."
        if not os.path.isdir(folder):
            return False, f"Cloud backup folder does not exist: {folder}"
        if not os.path.exists(_DB_PATH):
            return False, "Database file not found."

        try:
            self._checkpoint_wal()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = os.path.join(folder, f"dentnest_cloud_{timestamp}.db")
            shutil.copy2(_DB_PATH, dest_file)
            logger.info(f"Cloud backup created: {dest_file}")
            self._prune_cloud_backups(folder)
            return True, dest_file
        except Exception as e:
            logger.warning(f"Cloud backup failed: {e}")
            return False, str(e)

    # ── restore & merge ─────────────────────────────────────────────────

    def restore_backup(self, source_path: str) -> tuple[bool, str]:
        """Replace current DB with the given backup file.

        1. Validate source
        2. Auto-backup current DB as safety net
        3. Close current connection (flushes WAL)
        4. Overwrite DB file + remove stale WAL/SHM
        5. Next DB access auto-reconnects via singleton
        """
        ok, msg = self._validate_dentnest_db(source_path)
        if not ok:
            return False, msg

        try:
            # Safety-net backup of current DB
            self.auto_backup()

            # Close connection — this checkpoints WAL
            from ..database.db_manager import DatabaseManager
            DatabaseManager().close()

            # Replace the DB file
            shutil.copy2(source_path, _DB_PATH)

            # Remove stale WAL/SHM files so SQLite starts fresh
            for ext in ("-wal", "-shm"):
                sidecar = _DB_PATH + ext
                if os.path.exists(sidecar):
                    os.remove(sidecar)

            logger.info(f"Database restored from: {source_path}")
            return True, "Database restored successfully."
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False, f"Restore failed: {e}"

    def smart_merge(self, source_path: str) -> tuple[bool, dict]:
        """Import new records from source DB without losing existing data.

        Returns (success, stats_dict) where stats_dict has counts of
        imported records per table.
        """
        ok, msg = self._validate_dentnest_db(source_path)
        if not ok:
            return False, {"error": msg}

        stats = {
            "treatment_types": 0, "medicines": 0, "patients": 0,
            "treatments": 0, "payments": 0, "prescriptions": 0,
        }

        try:
            # Safety-net backup
            self.auto_backup()

            # Open source read-only
            src = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
            src.row_factory = sqlite3.Row

            # Current DB via DatabaseManager
            from ..database.db_manager import DatabaseManager
            conn = DatabaseManager().get_connection()

            # ── Phase 1: treatment_types (match by name) ──────────────
            tt_id_map: dict[int, int] = {}
            for row in src.execute("SELECT * FROM treatment_types"):
                existing = conn.execute(
                    "SELECT id FROM treatment_types WHERE name = ?",
                    (row["name"],)
                ).fetchone()
                if existing:
                    tt_id_map[row["id"]] = existing["id"]
                else:
                    cur = conn.execute(
                        "INSERT INTO treatment_types (name, default_cost) VALUES (?, ?)",
                        (row["name"], row["default_cost"])
                    )
                    tt_id_map[row["id"]] = cur.lastrowid
                    stats["treatment_types"] += 1

            # ── Phase 1b: medicines (match by name) ───────────────────
            for row in src.execute("SELECT * FROM medicines"):
                existing = conn.execute(
                    "SELECT id FROM medicines WHERE name = ?",
                    (row["name"],)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO medicines (name) VALUES (?)",
                        (row["name"],)
                    )
                    stats["medicines"] += 1

            # ── Phase 2: patients (match by name + mobile_number) ─────
            patient_id_map: dict[int, int] = {}
            for row in src.execute("SELECT * FROM patients"):
                existing = conn.execute(
                    "SELECT id FROM patients WHERE name = ? AND mobile_number = ?",
                    (row["name"], row["mobile_number"])
                ).fetchone()
                if existing:
                    patient_id_map[row["id"]] = existing["id"]
                else:
                    cur = conn.execute(
                        "INSERT INTO patients "
                        "(name, age, gender, mobile_number, address, medical_history, notes, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (row["name"], row["age"], row["gender"],
                         row["mobile_number"], row["address"],
                         row["medical_history"], row["notes"],
                         row["created_at"])
                    )
                    patient_id_map[row["id"]] = cur.lastrowid
                    stats["patients"] += 1

            # ── Phase 3: treatments (for all mapped patients) ─────────
            treatment_id_map: dict[int, int] = {}
            for row in src.execute("SELECT * FROM treatments"):
                src_patient_id = row["patient_id"]
                src_tt_id = row["treatment_type_id"]

                # Skip orphans
                if src_patient_id not in patient_id_map:
                    continue
                if src_tt_id not in tt_id_map:
                    continue

                mapped_pid = patient_id_map[src_patient_id]
                mapped_ttid = tt_id_map[src_tt_id]

                existing = conn.execute(
                    "SELECT id FROM treatments "
                    "WHERE patient_id = ? AND treatment_type_id = ? "
                    "AND start_date = ? AND total_cost = ?",
                    (mapped_pid, mapped_ttid,
                     row["start_date"], row["total_cost"])
                ).fetchone()
                if existing:
                    treatment_id_map[row["id"]] = existing["id"]
                else:
                    cur = conn.execute(
                        "INSERT INTO treatments "
                        "(patient_id, treatment_type_id, start_date, "
                        "total_cost, status, notes, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (mapped_pid, mapped_ttid,
                         row["start_date"], row["total_cost"],
                         row["status"], row["notes"], row["created_at"])
                    )
                    treatment_id_map[row["id"]] = cur.lastrowid
                    stats["treatments"] += 1

            # ── Phase 4: payments ─────────────────────────────────────
            for row in src.execute("SELECT * FROM payments"):
                src_tid = row["treatment_id"]
                if src_tid not in treatment_id_map:
                    continue
                mapped_tid = treatment_id_map[src_tid]

                existing = conn.execute(
                    "SELECT id FROM payments "
                    "WHERE treatment_id = ? AND amount = ? AND payment_date = ?",
                    (mapped_tid, row["amount"], row["payment_date"])
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO payments "
                        "(treatment_id, amount, payment_date, payment_method, notes) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (mapped_tid, row["amount"], row["payment_date"],
                         row["payment_method"], row["notes"])
                    )
                    stats["payments"] += 1

            # ── Phase 5: prescriptions ────────────────────────────────
            for row in src.execute("SELECT * FROM prescriptions"):
                src_tid = row["treatment_id"]
                if src_tid not in treatment_id_map:
                    continue
                mapped_tid = treatment_id_map[src_tid]

                existing = conn.execute(
                    "SELECT id FROM prescriptions "
                    "WHERE treatment_id = ? AND medicine_name = ? "
                    "AND prescribed_date = ? AND session_id = ?",
                    (mapped_tid, row["medicine_name"],
                     row["prescribed_date"], row["session_id"])
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO prescriptions "
                        "(treatment_id, medicine_name, dosage, frequency, "
                        "duration, notes, prescribed_date, session_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (mapped_tid, row["medicine_name"], row["dosage"],
                         row["frequency"], row["duration"], row["notes"],
                         row["prescribed_date"], row["session_id"])
                    )
                    stats["prescriptions"] += 1

            conn.commit()
            src.close()
            logger.info(f"Smart merge completed: {stats}")
            return True, stats

        except Exception as e:
            logger.error(f"Smart merge failed: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            try:
                src.close()
            except Exception:
                pass
            return False, {"error": str(e)}

    # ── internal ─────────────────────────────────────────────────────────

    def _prune_old_backups(self):
        """Delete oldest auto-backups beyond _MAX_AUTO_BACKUPS."""
        try:
            backups = sorted(
                Path(_AUTO_BACKUP_DIR).glob("auto_*.db"),
                key=lambda p: p.stat().st_mtime
            )
            while len(backups) > _MAX_AUTO_BACKUPS:
                oldest = backups.pop(0)
                oldest.unlink()
                logger.info(f"Pruned old auto-backup: {oldest}")
        except Exception as e:
            logger.warning(f"Failed to prune old backups: {e}")

    def _prune_cloud_backups(self, folder: str):
        """Delete oldest cloud backups beyond _MAX_AUTO_BACKUPS."""
        try:
            backups = sorted(
                Path(folder).glob("dentnest_cloud_*.db"),
                key=lambda p: p.stat().st_mtime
            )
            while len(backups) > _MAX_AUTO_BACKUPS:
                oldest = backups.pop(0)
                oldest.unlink()
                logger.info(f"Pruned old cloud backup: {oldest}")
        except Exception as e:
            logger.warning(f"Failed to prune cloud backups: {e}")
