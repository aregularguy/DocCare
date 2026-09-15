"""Service layer for dental chart (Odontogram) — tooth condition CRUD."""
import logging
from datetime import date
from typing import Optional
from ..database.db_manager import DatabaseManager
from ..models.tooth_condition import ToothCondition

logger = logging.getLogger(__name__)


class DentalChartService:
    """Handles saving and loading per-patient tooth conditions."""

    def __init__(self):
        self.db = DatabaseManager()

    # ── Ensure table exists (called from migrations too) ───────────────────

    def ensure_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tooth_conditions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id    INTEGER NOT NULL,
                tooth_number  INTEGER NOT NULL,
                condition     TEXT    NOT NULL DEFAULT 'healthy',
                notes         TEXT    DEFAULT '',
                recorded_date DATE,
                updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                UNIQUE (patient_id, tooth_number)
            )
        """)

    # ── Read ────────────────────────────────────────────────────────────────

    def get_patient_chart(self, patient_id: int) -> dict[int, ToothCondition]:
        """Return {tooth_number: ToothCondition} for all recorded teeth."""
        self.ensure_table()
        rows = self.db.fetch_all(
            "SELECT * FROM tooth_conditions WHERE patient_id = ? ORDER BY tooth_number",
            (patient_id,)
        )
        result = {}
        for row in rows:
            tc = ToothCondition(
                id=row["id"],
                patient_id=row["patient_id"],
                tooth_number=row["tooth_number"],
                condition=row["condition"],
                notes=row["notes"] or "",
                recorded_date=row["recorded_date"],
                updated_at=row["updated_at"],
            )
            result[tc.tooth_number] = tc
        return result

    # ── Write ───────────────────────────────────────────────────────────────

    def save_tooth(self, patient_id: int, tooth_number: int,
                   condition: str, notes: str = "") -> bool:
        """Insert or update a single tooth condition. Returns True on success."""
        self.ensure_table()
        try:
            today = date.today().isoformat()
            self.db.execute("""
                INSERT INTO tooth_conditions
                    (patient_id, tooth_number, condition, notes, recorded_date, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(patient_id, tooth_number)
                DO UPDATE SET
                    condition     = excluded.condition,
                    notes         = excluded.notes,
                    recorded_date = excluded.recorded_date,
                    updated_at    = CURRENT_TIMESTAMP
            """, (patient_id, tooth_number, condition, notes, today))
            return True
        except Exception as e:
            logger.error(f"Failed to save tooth {tooth_number}: {e}")
            return False

    def reset_tooth(self, patient_id: int, tooth_number: int) -> bool:
        """Reset a tooth back to 'healthy' (delete its record)."""
        self.ensure_table()
        try:
            self.db.execute(
                "DELETE FROM tooth_conditions WHERE patient_id=? AND tooth_number=?",
                (patient_id, tooth_number)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to reset tooth {tooth_number}: {e}")
            return False
