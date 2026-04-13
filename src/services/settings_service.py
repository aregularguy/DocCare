"""Clinic & doctor settings — persisted as JSON in data/settings.json."""
import json
import os
import tempfile
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
    "clinic_name_english": "",
    "clinic_name_marathi": "",
    "clinic_address": "",
    "clinic_phone": "",
    "clinic_timing": "",
    "doctor_name": "",
    "degree": "",
    "reg_number": "",
    "logo_path": "",
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
        data.update(self._read())
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
