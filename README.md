# DentNest - Dental Practice Management System

A comprehensive offline Windows desktop application for dental practice management built with Python and PyQt6.

## Features

### Patient Management
- Create and manage patient records
- Store patient information: Name, Mobile Number, Age, City/Address
- Search patients by name, mobile, or city
- View complete patient history

### Treatment Management
- Track various treatment types (Root Canal, Filling, Cleaning, Extraction, Crown, Implant, etc.)
- Set treatment costs and monitor status
- Add treatment notes and track progress
- Link treatments to specific patients

### Payment Tracking
- Record partial and full payments
- Automatic calculation of pending amounts
- Payment history per treatment
- Support multiple payment methods (Cash, Card, UPI, etc.)

### Prescription Management
- Add multiple medicines per visit
- Medicine autocomplete from database
- Specify dosage, frequency, and duration
- View prescription history

### Analytics Dashboard
- Daily, Weekly, Monthly, and Annual reports
- Patient metrics (total, new patients)
- Payment tracking and analysis
- Treatment type distribution
- Medicine prescription statistics
- Visual charts and graphs

## Technology Stack

- **Python 3.10+**: Core language
- **PyQt6**: Desktop UI framework
- **SQLite**: Offline database
- **Matplotlib**: Analytics charts
- **Pandas**: Data analysis

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone or download the project:
```bash
cd /path/to/DentNest
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Ensure virtual environment is activated
2. Run the application:
```bash
python src/main.py
```

## Building Executable

To create a standalone Windows executable:

```bash
pyinstaller --onefile --windowed --name DentNest src/main.py
```

The executable will be created in the `dist/` folder.

## Project Structure

```
DentNest/
├── src/
│   ├── main.py                      # Application entry point
│   ├── database/                    # Database layer
│   │   ├── db_manager.py           # SQLite connection manager
│   │   ├── migrations.py           # Schema creation
│   │   └── seed_data.py            # Initial data
│   ├── models/                      # Data classes
│   ├── repositories/                # Data access layer
│   ├── services/                    # Business logic layer
│   ├── ui/                          # User interface
│   │   ├── main_window.py          # Main application window
│   │   ├── widgets/                # UI components
│   │   └── dialogs/                # Dialog windows
│   └── utils/                       # Utility functions
├── data/                            # Database storage
├── tests/                           # Unit tests
└── requirements.txt                 # Python dependencies
```

## Database

The application uses SQLite for data storage. The database file is created automatically in the `data/` folder on first run.

### Tables
- **patients**: Patient information
- **treatment_types**: Available treatment types
- **treatments**: Patient treatments
- **payments**: Payment records
- **prescriptions**: Prescription details
- **medicines**: Medicine database for autocomplete

## Usage Guide

### Adding a Patient
1. Click "Patients" in the sidebar
2. Click "Add New Patient"
3. Fill in patient details (Name, Mobile, Age, City)
4. Click "Save"

### Adding a Treatment
1. Select a patient from the list
2. Click "Add Treatment"
3. Choose treatment type
4. Enter total cost
5. Add notes if needed
6. Click "Save"

### Recording Payment
1. View patient details
2. Select the treatment
3. Click "Add Payment"
4. Enter payment amount and method
5. Click "Save"

### Adding Prescription
1. Open patient treatment
2. Click "Add Prescription"
3. Enter medicine details (name, dosage, frequency, duration)
4. Add multiple medicines as needed
5. Click "Save"

### Viewing Analytics
1. Click "Analytics" in the sidebar
2. Select date range (Today, This Week, This Month, This Year)
3. View metrics and charts

## Backup

The database file (`data/dentnest.db`) can be backed up by simply copying the file to a safe location.

### Automatic Backup (Recommended)
Copy the database file daily to a backup location.

### Manual Backup
1. Close the application
2. Copy `data/dentnest.db` to backup location
3. Restart the application

## Support

For issues or questions, please contact your system administrator.

## License

Proprietary - For internal use only

## Version

Version 1.0.0 - Initial Release
# DocCare
