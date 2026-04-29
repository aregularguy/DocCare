"""Clinic & doctor settings — persisted as JSON in data/settings.json."""
import json
import os
import tempfile
import hashlib
import secrets
import string
import logging
from typing import Optional

logger = logging.getLogger(__name__)

import sys as _sys
if getattr(_sys, 'frozen', False):
    # Running as PyInstaller .exe — store settings next to the .exe
    _DATA_DIR = os.path.join(os.path.dirname(_sys.executable), "data")
else:
    _DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data"
    )
_SETTINGS_PATH = os.path.join(_DATA_DIR, "settings.json")

_DEFAULTS = {
    "clinic_name_english": "Dr. Abrar's Dental Care and Implant Centre",
    "clinic_name_marathi": "दातांचा दवाखाना",
    "clinic_address":      "Plot 12, Main Road, Phaltan, Maharashtra",
    "clinic_phone":        "7620962937 / 7588606132",
    "clinic_timing":       "सकाळी ९ ते दुपारी २  |  सायं. ५ ते रात्री ८",
    "doctor_name":         "Dr. Abrar Pharuk Shaikh",
    "degree":              "B.D.S (RGUHS)",
    "reg_number":          "A-51710",
    "logo_path":           "",
    "app_password_hash":   "",   # SHA-256 hex of the login password; empty = no lock
    "recovery_key_hash":   "",   # SHA-256 hex of recovery key; empty = none
    "cloud_backup_folder": "",   # Path to cloud-synced folder for auto-backup
}


class SettingsService:
    """Read and write clinic/doctor settings."""

    def __init__(self):
        os.makedirs(os.path.dirname(_SETTINGS_PATH), exist_ok=True)
        if not os.path.exists(_SETTINGS_PATH):
            self._write(_DEFAULTS.copy())

    # ── public API ─────────────────────────────────────────────────────

    def get_all(self) -> dict:
        data = _DEFAULTS.copy()
        # Only override defaults with saved values that are non-empty,
        # so defaults always show on a fresh install or for unset fields.
        saved = self._read()
        for k, v in saved.items():
            if k in data and v != "":
                data[k] = v
            elif k not in data:
                data[k] = v   # keep unknown keys (e.g. password hashes)
        return data

    def get(self, key: str, fallback: str = "") -> str:
        return self.get_all().get(key, fallback)

    def save(self, data: dict) -> bool:
        try:
            current = self._read()
            current.update({k: v for k, v in data.items() if k in _DEFAULTS})
            self._write(current)
            return True
        except Exception:
            return False

    # ── password helpers ───────────────────────────────────────────────

    def is_password_set(self) -> bool:
        return bool(self.get("app_password_hash"))

    def set_password(self, plain_password: str) -> bool:
        """Hash and store a new password. Pass empty string to remove."""
        hashed = hashlib.sha256(plain_password.encode()).hexdigest() if plain_password else ""
        return self.save({"app_password_hash": hashed})

    def verify_password(self, plain_password: str) -> bool:
        stored = self.get("app_password_hash")
        if not stored:
            return True  # no password set = always allow
        return hashlib.sha256(plain_password.encode()).hexdigest() == stored

    # ── recovery key helpers ───────────────────────────────────────────

    def generate_recovery_key(self) -> str:
        """Generate a random 12-char recovery key, store its hash, return plaintext.

        Format: XXX-XXX-XXX-XXX (uppercase alphanumeric).
        """
        raw = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
        formatted = '-'.join(raw[i:i+3] for i in range(0, 12, 3))
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        self.save({"recovery_key_hash": hashed})
        return formatted

    def verify_recovery_key(self, key: str) -> bool:
        """Verify a recovery key against the stored hash."""
        stored = self.get("recovery_key_hash")
        if not stored:
            return False
        clean = key.replace('-', '').replace(' ', '').upper()
        return hashlib.sha256(clean.encode()).hexdigest() == stored

    # ── internal ───────────────────────────────────────────────────────

    def _read(self) -> dict:
        if not os.path.exists(_SETTINGS_PATH):
            return {}
        try:
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Settings file is corrupted ({e}), using defaults")
            return {}
        except Exception as e:
            logger.error(f"Failed to read settings: {e}")
            return {}

    def _write(self, data: dict):
        # Atomic write: write to temp file, then rename
        dir_name = os.path.dirname(_SETTINGS_PATH)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, _SETTINGS_PATH)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
