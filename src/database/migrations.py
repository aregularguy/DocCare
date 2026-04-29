"""Database schema migrations for DentNest."""
import logging
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables if they don't exist."""
    db = DatabaseManager()

    logger.info("Creating database tables...")

    # Patients table
    db.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Treatment types table
    db.execute("""
        CREATE TABLE IF NOT EXISTS treatment_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    # Treatments table
    db.execute("""
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            treatment_type_id INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'planned',
            start_date DATE,
            completion_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
            FOREIGN KEY (treatment_type_id) REFERENCES treatment_types(id),
            CHECK (status IN ('planned', 'in_progress', 'completed'))
        )
    """)

    # Payments table
    db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            treatment_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            payment_method TEXT DEFAULT 'cash',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE,
            CHECK (payment_method IN ('cash', 'card', 'upi', 'cheque', 'other'))
        )
    """)

    # Prescriptions table
    db.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            treatment_id INTEGER NOT NULL,
            session_id TEXT,
            medicine_name TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            prescribed_date DATE NOT NULL,
            notes TEXT,
            FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE
        )
    """)

    # Migrate: add session_id if missing (for existing databases)
    try:
        db.execute("ALTER TABLE prescriptions ADD COLUMN session_id TEXT")
        logger.info("Migrated prescriptions table: added session_id column")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            pass  # column already exists, expected
        else:
            logger.error(f"Migration failed for session_id column: {e}")
            raise

    # Migrate: add X-Ray treatment type if missing (works on existing databases)
    db.execute("""
        INSERT OR IGNORE INTO treatment_types (name, description)
        VALUES
            ('X-Ray',        'Dental X-Ray imaging and diagnosis'),
            ('Consultation',  'General dental consultation')
    """)

    # Medicines table (for autocomplete suggestions)
    db.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            common_dosage TEXT,
            category TEXT
        )
    """)

    # Migrate: add medicine_type and brand_name to medicines table
    for col in ('medicine_type', 'brand_name'):
        try:
            db.execute(f"ALTER TABLE medicines ADD COLUMN {col} TEXT")
            logger.info(f"Migrated medicines table: added {col} column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                pass  # column already exists, expected
            else:
                logger.error(f"Migration failed for {col} column: {e}")
                raise

    # Create indexes for better query performance
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_patients_name
        ON patients(name)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_patients_mobile
        ON patients(mobile_number)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_treatments_patient
        ON treatments(patient_id)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_treatment
        ON payments(treatment_id)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_payments_date
        ON payments(payment_date)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_prescriptions_treatment
        ON prescriptions(treatment_id)
    """)

    # Create trigger to update patient's updated_at timestamp
    db.execute("""
        CREATE TRIGGER IF NOT EXISTS update_patient_timestamp
        AFTER UPDATE ON patients
        BEGIN
            UPDATE patients SET updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.id;
        END
    """)

    logger.info("Database tables created successfully")


def drop_all_tables():
    """Drop all tables (use with caution - for testing only)."""
    db = DatabaseManager()

    logger.warning("Dropping all database tables...")

    tables = [
        'prescriptions',
        'payments',
        'treatments',
        'treatment_types',
        'medicines',
        'patients'
    ]

    for table in tables:
        db.execute(f"DROP TABLE IF EXISTS {table}")

    logger.warning("All tables dropped")


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create tables
    create_tables()
    print("Database schema created successfully!")
