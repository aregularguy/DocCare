"""Seed initial data for DentNest database."""
import logging
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)


def seed_treatment_types():
    """Add default treatment types."""
    db = DatabaseManager()

    treatment_types = [
        ('Root Canal', 'Endodontic treatment to remove infected pulp'),
        ('Filling', 'Dental filling for cavities'),
        ('Cleaning', 'Professional teeth cleaning and scaling'),
        ('Extraction', 'Tooth removal procedure'),
        ('Crown', 'Dental crown or cap placement'),
        ('Implant', 'Dental implant surgery'),
        ('Whitening', 'Teeth whitening treatment'),
        ('Braces', 'Orthodontic braces installation'),
        ('Denture', 'Removable denture fitting'),
        ('Veneer', 'Dental veneer application'),
        ('Bridge', 'Dental bridge placement'),
        ('Consultation', 'General dental consultation'),
    ]

    # Use INSERT OR IGNORE so missing types are always added
    # (even if some already exist from migration or a partial import)
    db.executemany(
        "INSERT OR IGNORE INTO treatment_types (name, description) VALUES (?, ?)",
        treatment_types
    )

    logger.info(f"Ensured {len(treatment_types)} treatment types exist")


def seed_medicines():
    """Add common medicines to database."""
    db = DatabaseManager()

    # (name, common_dosage, category, medicine_type, brand_name)
    medicines = [
        # Antibiotics
        ('Amoxicillin 500mg', '500mg', 'antibiotic', 'capsule', ''),
        ('Azithromycin 500mg', '500mg', 'antibiotic', 'tablet', ''),
        ('Clindamycin 300mg', '300mg', 'antibiotic', 'capsule', ''),
        ('Metronidazole 400mg', '400mg', 'antibiotic', 'tablet', ''),

        # Painkillers
        ('Ibuprofen 400mg', '400mg', 'painkiller', 'tablet', ''),
        ('Paracetamol 500mg', '500mg', 'painkiller', 'tablet', ''),
        ('Diclofenac 50mg', '50mg', 'painkiller', 'tablet', ''),
        ('Ketorolac 10mg', '10mg', 'painkiller', 'tablet', ''),

        # Antiseptics and Mouthwash
        ('Chlorhexidine Mouthwash', '0.2%', 'antiseptic', 'mouthwash', ''),
        ('Betadine Gargle', '2%', 'antiseptic', 'mouthwash', ''),
        ('Hydrogen Peroxide Mouthwash', '3%', 'antiseptic', 'mouthwash', ''),

        # Anti-inflammatory
        ('Prednisolone 5mg', '5mg', 'anti-inflammatory', 'tablet', ''),
        ('Dexamethasone 0.5mg', '0.5mg', 'anti-inflammatory', 'tablet', ''),

        # Vitamins and Supplements
        ('Vitamin B Complex', 'standard', 'vitamin', 'tablet', ''),
        ('Calcium + Vitamin D3', 'standard', 'supplement', 'tablet', ''),

        # Topical Applications
        ('Lignocaine Gel 2%', '2%', 'topical', 'gel', ''),
        ('Clove Oil', 'standard', 'topical', 'liquid', ''),

        # Antifungal
        ('Fluconazole 150mg', '150mg', 'antifungal', 'capsule', ''),
        ('Nystatin Oral Drops', 'standard', 'antifungal', 'drops', ''),

        # Extended dental medicines — Antibiotics
        ('Amoxicillin + Clavulanate 625mg', '625mg', 'antibiotic', 'tablet', ''),
        ('Tinidazole 500mg', '500mg', 'antibiotic', 'tablet', ''),
        ('Doxycycline 100mg', '100mg', 'antibiotic', 'capsule', ''),

        # Painkillers / Anti-inflammatory
        ('Ibuprofen 600mg', '600mg', 'analgesic', 'tablet', ''),
        ('Paracetamol 650mg', '650mg', 'analgesic', 'tablet', ''),
        ('Aceclofenac 100mg', '100mg', 'analgesic', 'tablet', ''),
        ('Nimesulide 100mg', '100mg', 'analgesic', 'tablet', ''),
        ('Tramadol 50mg', '50mg', 'analgesic', 'capsule', ''),
        ('Ketorolac 10mg (analgesic)', '10mg', 'analgesic', 'tablet', ''),
        ('Diclofenac 50mg (analgesic)', '50mg', 'analgesic', 'tablet', ''),

        # Antifungal
        ('Clotrimazole Mouth Gel', 'standard', 'antifungal', 'gel', ''),
        ('Nystatin Oral Suspension', 'standard', 'antifungal', 'liquid', ''),

        # Mouthwash / Rinse
        ('Chlorhexidine 0.2% Mouthwash', '0.2%', 'antiseptic', 'mouthwash', ''),
        ('Povidone Iodine Gargle', 'standard', 'antiseptic', 'mouthwash', ''),
        ('Benzydamine Mouthwash', 'standard', 'anti-inflammatory', 'mouthwash', ''),

        # Topical / Anesthetic
        ('Lidocaine Gel 2%', '2%', 'anesthetic', 'gel', ''),
        ('Benzocaine Gel', 'standard', 'anesthetic', 'gel', ''),
        ('Triamcinolone Acetonide Paste', 'standard', 'corticosteroid', 'paste', ''),
        ('Choline Salicylate Gel', 'standard', 'analgesic', 'gel', ''),

        # Vitamins / Supplements
        ('Vitamin C 500mg', '500mg', 'supplement', 'tablet', ''),
        ('Zinc Supplement', 'standard', 'supplement', 'tablet', ''),

        # Antacids
        ('Pantoprazole 40mg', '40mg', 'antacid', 'tablet', ''),
        ('Omeprazole 20mg', '20mg', 'antacid', 'capsule', ''),
    ]

    # Backfill medicine_type for existing rows that lack it
    _backfill_medicine_types(db, medicines)

    # Batch check: fetch all existing medicine names in one query
    existing_rows = db.fetch_all("SELECT name FROM medicines")
    existing_names = {row['name'] for row in existing_rows}

    # Filter to only new medicines and batch insert
    new_medicines = [
        (name, common_dosage, category, medicine_type, brand_name)
        for name, common_dosage, category, medicine_type, brand_name in medicines
        if name not in existing_names
    ]

    if new_medicines:
        db.executemany(
            "INSERT INTO medicines (name, common_dosage, category, medicine_type, brand_name) VALUES (?, ?, ?, ?, ?)",
            new_medicines
        )
        logger.info(f"Seeded {len(new_medicines)} new medicines")
    else:
        logger.info("All medicines already exist, skipping seed")


def _backfill_medicine_types(db, medicines):
    """Backfill medicine_type for existing rows that already have medicines but lack the new column value."""
    for name, _dosage, _category, medicine_type, brand_name in medicines:
        db.execute(
            "UPDATE medicines SET medicine_type = ? WHERE name = ? AND (medicine_type IS NULL OR medicine_type = '')",
            (medicine_type, name)
        )


def seed_all():
    """Run all seed functions."""
    logger.info("Starting database seeding...")
    seed_treatment_types()
    seed_medicines()
    logger.info("Database seeding completed")


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Seed data
    seed_all()
    print("Database seeded successfully!")
