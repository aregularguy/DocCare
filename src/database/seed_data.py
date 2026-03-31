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

    # Check if data already exists
    existing = db.fetch_one("SELECT COUNT(*) as count FROM treatment_types")
    if existing and existing['count'] > 0:
        logger.info("Treatment types already exist, skipping seed")
        return

    # Insert treatment types
    db.executemany(
        "INSERT INTO treatment_types (name, description) VALUES (?, ?)",
        treatment_types
    )

    logger.info(f"Seeded {len(treatment_types)} treatment types")


def seed_medicines():
    """Add common medicines to database."""
    db = DatabaseManager()

    medicines = [
        # Antibiotics
        ('Amoxicillin 500mg', '500mg', 'antibiotic'),
        ('Azithromycin 500mg', '500mg', 'antibiotic'),
        ('Clindamycin 300mg', '300mg', 'antibiotic'),
        ('Metronidazole 400mg', '400mg', 'antibiotic'),

        # Painkillers
        ('Ibuprofen 400mg', '400mg', 'painkiller'),
        ('Paracetamol 500mg', '500mg', 'painkiller'),
        ('Diclofenac 50mg', '50mg', 'painkiller'),
        ('Ketorolac 10mg', '10mg', 'painkiller'),

        # Antiseptics and Mouthwash
        ('Chlorhexidine Mouthwash', '0.2%', 'antiseptic'),
        ('Betadine Gargle', '2%', 'antiseptic'),
        ('Hydrogen Peroxide Mouthwash', '3%', 'antiseptic'),

        # Anti-inflammatory
        ('Prednisolone 5mg', '5mg', 'anti-inflammatory'),
        ('Dexamethasone 0.5mg', '0.5mg', 'anti-inflammatory'),

        # Vitamins and Supplements
        ('Vitamin B Complex', 'standard', 'vitamin'),
        ('Calcium + Vitamin D3', 'standard', 'supplement'),

        # Topical Applications
        ('Lignocaine Gel 2%', '2%', 'topical'),
        ('Clove Oil', 'standard', 'topical'),

        # Antifungal
        ('Fluconazole 150mg', '150mg', 'antifungal'),
        ('Nystatin Oral Drops', 'standard', 'antifungal'),

        # Extended dental medicines — Antibiotics
        ('Amoxicillin + Clavulanate 625mg', '625mg', 'antibiotic'),
        ('Tinidazole 500mg', '500mg', 'antibiotic'),
        ('Doxycycline 100mg', '100mg', 'antibiotic'),

        # Painkillers / Anti-inflammatory
        ('Ibuprofen 600mg', '600mg', 'analgesic'),
        ('Paracetamol 650mg', '650mg', 'analgesic'),
        ('Aceclofenac 100mg', '100mg', 'analgesic'),
        ('Nimesulide 100mg', '100mg', 'analgesic'),
        ('Tramadol 50mg', '50mg', 'analgesic'),
        ('Ketorolac 10mg (analgesic)', '10mg', 'analgesic'),
        ('Diclofenac 50mg (analgesic)', '50mg', 'analgesic'),

        # Antifungal
        ('Clotrimazole Mouth Gel', 'standard', 'antifungal'),
        ('Nystatin Oral Suspension', 'standard', 'antifungal'),

        # Mouthwash / Rinse
        ('Chlorhexidine 0.2% Mouthwash', '0.2%', 'antiseptic'),
        ('Povidone Iodine Gargle', 'standard', 'antiseptic'),
        ('Benzydamine Mouthwash', 'standard', 'anti-inflammatory'),

        # Topical / Anesthetic
        ('Lidocaine Gel 2%', '2%', 'anesthetic'),
        ('Benzocaine Gel', 'standard', 'anesthetic'),
        ('Triamcinolone Acetonide Paste', 'standard', 'corticosteroid'),
        ('Choline Salicylate Gel', 'standard', 'analgesic'),

        # Vitamins / Supplements
        ('Vitamin C 500mg', '500mg', 'supplement'),
        ('Zinc Supplement', 'standard', 'supplement'),

        # Antacids
        ('Pantoprazole 40mg', '40mg', 'antacid'),
        ('Omeprazole 20mg', '20mg', 'antacid'),
    ]

    # Insert only medicines that don't already exist (check by name)
    inserted = 0
    for name, common_dosage, category in medicines:
        existing = db.fetch_one(
            "SELECT id FROM medicines WHERE name = ?", (name,)
        )
        if not existing:
            db.execute(
                "INSERT INTO medicines (name, common_dosage, category) VALUES (?, ?, ?)",
                (name, common_dosage, category)
            )
            inserted += 1

    if inserted > 0:
        logger.info(f"Seeded {inserted} new medicines")
    else:
        logger.info("All medicines already exist, skipping seed")


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
