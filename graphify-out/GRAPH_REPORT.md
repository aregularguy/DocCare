# Graph Report - .  (2026-04-22)

## Corpus Check
- Corpus is ~41,835 words - fits in a single context window. You may not need a graph.

## Summary
- 760 nodes · 2144 edges · 30 communities detected
- Extraction: 49% EXTRACTED · 51% INFERRED · 0% AMBIGUOUS · INFERRED: 1090 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Analytics Computations|Analytics Computations]]
- [[_COMMUNITY_Analytics Service API|Analytics Service API]]
- [[_COMMUNITY_Patient Details & Prescriptions|Patient Details & Prescriptions]]
- [[_COMMUNITY_Payment Dialogs & Cards|Payment Dialogs & Cards]]
- [[_COMMUNITY_Security & Audit Findings|Security & Audit Findings]]
- [[_COMMUNITY_Data Access Layer|Data Access Layer]]
- [[_COMMUNITY_Export & Main Window|Export & Main Window]]
- [[_COMMUNITY_Backup & Settings|Backup & Settings]]
- [[_COMMUNITY_Patient Forms|Patient Forms]]
- [[_COMMUNITY_Dashboard Charts|Dashboard Charts]]
- [[_COMMUNITY_Top Navigation Bar|Top Navigation Bar]]
- [[_COMMUNITY_App Entry Point|App Entry Point]]
- [[_COMMUNITY_Tests Module|Tests Module]]
- [[_COMMUNITY_Source Package|Source Package]]
- [[_COMMUNITY_Models Package|Models Package]]
- [[_COMMUNITY_Utils Package|Utils Package]]
- [[_COMMUNITY_Repositories Package|Repositories Package]]
- [[_COMMUNITY_UI Package|UI Package]]
- [[_COMMUNITY_Dialogs Package|Dialogs Package]]
- [[_COMMUNITY_Widgets Package|Widgets Package]]
- [[_COMMUNITY_Database Package|Database Package]]
- [[_COMMUNITY_Services Package|Services Package]]
- [[_COMMUNITY_Treatment Workflow|Treatment Workflow]]
- [[_COMMUNITY_Payment Processing|Payment Processing]]
- [[_COMMUNITY_Patient Repository|Patient Repository]]
- [[_COMMUNITY_Prescription Service|Prescription Service]]
- [[_COMMUNITY_Login Authentication|Login Authentication]]
- [[_COMMUNITY_Dashboard Widget|Dashboard Widget]]
- [[_COMMUNITY_Settings UI|Settings UI]]
- [[_COMMUNITY_Payment List Widget|Payment List Widget]]

## God Nodes (most connected - your core abstractions)
1. `PatientService` - 94 edges
2. `TreatmentService` - 89 edges
3. `DatabaseManager` - 63 edges
4. `Patient` - 58 edges
5. `BaseRepository` - 56 edges
6. `TreatmentRepository` - 48 edges
7. `PrescriptionService` - 46 edges
8. `PatientDetailsWidget` - 42 edges
9. `SettingsService` - 41 edges
10. `PaymentService` - 39 edges

## Surprising Connections (you probably didn't know these)
- `DentNest App Icon` ----> `DentNest`  [EXTRACTED]
  src/resources/icons/dentnest.png → README.md
- `Clinic Logo (Caduceus)` ----> `DentNest`  [EXTRACTED]
  data/clinic_logo.png → README.md
- `Clinic Logo (Caduceus)` ----> `Prescription Management`  [EXTRACTED]
  data/clinic_logo.png → README.md
- `DentNest App Icon` ----> `Cursor-Inspired UI Design`  [EXTRACTED]
  src/resources/icons/dentnest.png → claude.md
- `Get all records.          Returns:             List of model instances` --uses--> `DatabaseManager`  [INFERRED]
  src/repositories/base_repository.py → src/database/db_manager.py

## Communities

### Community 0 - "Analytics Computations"
Cohesion: 0.03
Nodes (96): Analytics business logic service., Get treatment metrics for date range.          Args:             start_date: Sta, Service for analytics and reporting., Get prescription metrics for date range.          Args:             start_date:, Initialize analytics service., Get complete dashboard data for a period.          Args:             period: One, Get daily payment totals for charting.          Args:             start_date: St, Get date range for a period.          Args:             period: One of 'today', (+88 more)

### Community 1 - "Analytics Service API"
Cohesion: 0.05
Nodes (34): AnalyticsService, Count total records.          Returns:             Number of records, DashboardWidget, MetricCard, Dashboard widget - Home screen with quick stats., Create the metrics grid with cards., Create recent activity section., Card widget for displaying a single metric. (+26 more)

### Community 2 - "Patient Details & Prescriptions"
Cohesion: 0.07
Nodes (20): format_currency(), Format amount as currency.      Args:         amount: Amount to format      Retu, PatientDetailsWidget, Initialize the form UI., PatientFormView, PatientListWidget, Load patient data into form., Inline patient form (not a dialog). (+12 more)

### Community 3 - "Payment Dialogs & Cards"
Cohesion: 0.07
Nodes (39): AddPaymentDialog, ClickableCard, _PrescriptionRowWidget, Patient details widget - embedded in main window (SimplePractice style)., Payment entry dialog., One medicine row: Medicine | M-A-E-N spinboxes | Timing | Quantity., Rebuild the overview tab content in-place.          Guard against re-entrant cal, A QFrame that triggers a callback when clicked. (+31 more)

### Community 4 - "Security & Audit Findings"
Cohesion: 0.04
Nodes (68): Analytics Dashboard, Arshad Bagwan, Attack Chain: Insider Data Theft, Attack Chain: Complete Data Breach (Stolen Laptop), HTML Injection in Prescription PDF (Bug #6), No Transaction Rollback on DB Errors (Bug #4), Race Condition in Payment Addition (Bug #1), SQL Injection Pattern in Repositories (Bug #17) (+60 more)

### Community 5 - "Data Access Layer"
Cohesion: 0.06
Nodes (37): Get all records.          Returns:             List of model instances, Fetch all rows from query.          Args:             query: SQL query string, from_db_row(), Medicine, Convert to dictionary., String representation., Search patients by name, mobile, or city.          Args:             query: Sear, Get recently added or updated patients.          Args:             limit: Maximu (+29 more)

### Community 6 - "Export & Main Window"
Cohesion: 0.07
Nodes (22): ExportDataWidget, Export data widget - Placeholder., NavItem, Main application window with sidebar navigation., Public alias kept for compatibility with other widgets., Main application window., Vertical icon + label nav item — TatvaPractice style., Initialize the main window UI. (+14 more)

### Community 7 - "Backup & Settings"
Cohesion: 0.06
Nodes (27): BackupService, Database backup service — manual and auto-backup., Delete oldest auto-backups beyond _MAX_AUTO_BACKUPS., Handles database backup operations., Copy the DB to destination_folder with a timestamp filename.          Returns (s, Create an automatic backup in data/backups/ — called on app startup.          Ke, Return info about the most recent backup (auto or manual)., Return DB file size as a human-readable string. (+19 more)

### Community 8 - "Patient Forms"
Cohesion: 0.06
Nodes (34): PatientFormDialog, Patient form dialog for add/edit operations., Load patient data into form fields., Handle save button click., Dialog for adding or editing patient information., Patient list and management widget with inline form., Patient, Convert to dictionary.          Returns:             Dictionary representation (+26 more)

### Community 9 - "Dashboard Charts"
Cohesion: 0.09
Nodes (17): AnalyticsDashboardWidget, ChartCard, MetricCard, PeriodSelector, Analytics dashboard — clean, well-sized charts with proper styling., Chart container with title and matplotlib canvas., format_date(), format_datetime() (+9 more)

### Community 10 - "Top Navigation Bar"
Cohesion: 0.27
Nodes (3): LogoButton, Top navigation bar widget., Clickable logo — shows image or purple initials placeholder.

### Community 11 - "App Entry Point"
Cohesion: 1.0
Nodes (1): PyInstaller entry point — avoids relative import issues.

### Community 12 - "Tests Module"
Cohesion: 1.0
Nodes (0): 

### Community 13 - "Source Package"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Models Package"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Utils Package"
Cohesion: 1.0
Nodes (1): Create TreatmentType instance from database row.

### Community 16 - "Repositories Package"
Cohesion: 1.0
Nodes (1): Create Treatment instance from database row.

### Community 17 - "UI Package"
Cohesion: 1.0
Nodes (1): Calculate pending payment amount.

### Community 18 - "Dialogs Package"
Cohesion: 1.0
Nodes (1): Check if treatment is fully paid.

### Community 19 - "Widgets Package"
Cohesion: 1.0
Nodes (1): Create Payment instance from database row.

### Community 20 - "Database Package"
Cohesion: 1.0
Nodes (1): Create Patient instance from database row.          Args:             row: SQLit

### Community 21 - "Services Package"
Cohesion: 1.0
Nodes (1): Create Prescription instance from database row.

### Community 22 - "Treatment Workflow"
Cohesion: 1.0
Nodes (1): Create Medicine instance from database row.

### Community 23 - "Payment Processing"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Patient Repository"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Prescription Service"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Login Authentication"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Dashboard Widget"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Settings UI"
Cohesion: 1.0
Nodes (0): 

### Community 29 - "Payment List Widget"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **86 isolated node(s):** `PyInstaller entry point — avoids relative import issues.`, `Treatment data model.`, `Treatment type data model.`, `Create TreatmentType instance from database row.`, `String representation.` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `App Entry Point`** (2 nodes): `app.py`, `PyInstaller entry point — avoids relative import issues.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Tests Module`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Source Package`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Models Package`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Utils Package`** (1 nodes): `Create TreatmentType instance from database row.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Repositories Package`** (1 nodes): `Create Treatment instance from database row.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Package`** (1 nodes): `Calculate pending payment amount.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dialogs Package`** (1 nodes): `Check if treatment is fully paid.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Widgets Package`** (1 nodes): `Create Payment instance from database row.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Database Package`** (1 nodes): `Create Patient instance from database row.          Args:             row: SQLit`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Services Package`** (1 nodes): `Create Prescription instance from database row.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Treatment Workflow`** (1 nodes): `Create Medicine instance from database row.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Payment Processing`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Patient Repository`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Prescription Service`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Login Authentication`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Widget`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Settings UI`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Payment List Widget`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Matplotlib` connect `Security & Audit Findings` to `Dashboard Charts`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `TreatmentService` connect `Payment Dialogs & Cards` to `Analytics Computations`, `Analytics Service API`, `Patient Details & Prescriptions`, `Export & Main Window`, `Backup & Settings`, `Patient Forms`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 83 inferred relationships involving `PatientService` (e.g. with `RecordPaymentDialog` and `PaymentListWidget`) actually correct?**
  _`PatientService` has 83 INFERRED edges - model-reasoned connections that need verification._
- **Are the 80 inferred relationships involving `TreatmentService` (e.g. with `ClickableCard` and `PatientDetailsWidget`) actually correct?**
  _`TreatmentService` has 80 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `DatabaseManager` (e.g. with `BaseRepository` and `Base repository with generic CRUD operations.`) actually correct?**
  _`DatabaseManager` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 55 inferred relationships involving `Patient` (e.g. with `PatientRepository` and `Repository for patient data access.`) actually correct?**
  _`Patient` has 55 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `BaseRepository` (e.g. with `DatabaseManager` and `TreatmentTypeRepository`) actually correct?**
  _`BaseRepository` has 46 INFERRED edges - model-reasoned connections that need verification._