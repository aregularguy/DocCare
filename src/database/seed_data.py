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
    ]

    # Check if data already exists
    existing = db.fetch_one("SELECT COUNT(*) as count FROM medicines")
    if existing and existing['count'] > 0:
        logger.info("Medicines already exist, skipping seed")
        return

    # Insert medicines
    db.executemany(
        "INSERT INTO medicines (name, common_dosage, category) VALUES (?, ?, ?)",
        medicines
    )

    logger.info(f"Seeded {len(medicines)} medicines")


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
