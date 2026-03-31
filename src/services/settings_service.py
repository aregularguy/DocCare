"""Clinic & doctor settings — persisted as JSON in data/settings.json."""
import json
import os
from typing import Optional

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
        try:
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write(self, data: dict):
        with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
