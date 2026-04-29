"""Database backup service — manual and auto-backup."""
import os
import shutil
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


class BackupService:
    """Handles database backup operations."""

    # ── public API ────────────────────────────────────────────────────────

    def backup_now(self, destination_folder: str) -> tuple[bool, str]:
        """Copy the DB to destination_folder with a timestamp filename.

        Returns (success, message/path).
        """
        if not os.path.exists(_DB_PATH):
            return False, "Database file not found. Nothing to backup."

        try:
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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = os.path.join(folder, f"dentnest_cloud_{timestamp}.db")
            shutil.copy2(_DB_PATH, dest_file)
            logger.info(f"Cloud backup created: {dest_file}")
            self._prune_cloud_backups(folder)
            return True, dest_file
        except Exception as e:
            logger.warning(f"Cloud backup failed: {e}")
            return False, str(e)

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
