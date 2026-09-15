"""Tooth condition data model for the dental chart (Odontogram)."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import date


# FDI tooth numbering system: upper right 11-18, upper left 21-28,
# lower left 31-38, lower right 41-48.
FDI_UPPER = list(range(11, 19)) + list(range(21, 29))  # 11-18, 21-28
FDI_LOWER = list(range(31, 39)) + list(range(41, 49))  # 31-38, 41-48
ALL_TEETH = FDI_UPPER + FDI_LOWER

# Possible conditions a tooth can have
TOOTH_CONDITIONS = {
    "healthy":      {"label": "Healthy",      "color": "#FFFFFF", "border": "#34C759", "text": "#34C759"},
    "decay":        {"label": "Decay/Cavity", "color": "#FF6B6B", "border": "#FF3B30", "text": "#FF3B30"},
    "filled":       {"label": "Filled",       "color": "#FFE082", "border": "#FF9500", "text": "#774E00"},
    "crown":        {"label": "Crown",        "color": "#B39DDB", "border": "#5856D6", "text": "#5856D6"},
    "missing":      {"label": "Missing",      "color": "#E0E0E0", "border": "#86868B", "text": "#86868B"},
    "implant":      {"label": "Implant",      "color": "#80DEEA", "border": "#00B0C8", "text": "#005F6A"},
    "root_canal":   {"label": "Root Canal",   "color": "#FFCCBC", "border": "#FF6D00", "text": "#BF360C"},
    "extraction":   {"label": "For Extraction","color": "#EF9A9A","border": "#E53935", "text": "#B71C1C"},
    "bridge":       {"label": "Bridge",       "color": "#C8E6C9", "border": "#34C759", "text": "#1B5E20"},
}


@dataclass
class ToothCondition:
    """Represents the recorded condition of a single tooth for a patient."""
    id: Optional[int] = None
    patient_id: int = 0
    tooth_number: int = 0          # FDI number e.g. 11, 22, 36
    condition: str = "healthy"     # key from TOOTH_CONDITIONS
    notes: str = ""
    recorded_date: Optional[date] = None
    updated_at: Optional[str] = None
