# Lab Management System

A comprehensive system for managing computer labs, equipment, and resources at Islamic University of Madinah. The system handles lab bookings, equipment maintenance, and inventory management with role-based access control.

## Features

### Lab Management
- View available labs and their current status
- Real-time lab availability tracking
- Book labs for specific time slots
- Lab booking approval workflow
- Lab access control based on approved bookings
- Current lab status tracking (available/in use)

### Equipment Management
- Equipment inventory tracking
- Equipment maintenance request system
- Issue reporting and resolution workflow
- Equipment status monitoring (operational/maintenance required)
- Equipment addition and removal tracking
- Equipment history tracking

### User Management
- Role-based access control
- Multiple user roles:
  - Administrator: Full system access
  - Student: Lab booking and equipment requests
  - IT Staff: Equipment maintenance and management
  - Instructor: Lab booking and access

### Inventory System
- Equipment request management
- Purchase request workflow
- Inventory status tracking
- IT staff notifications for new equipment

## Project Structure
```
lab_management_system/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── README.md             # Project documentation
├── database/
│   ├── schema_updates.sql    # Database schema
│   └── database_setup.py     # Database initialization
├── modules/
│   ├── __init__.py
│   ├── error_handling.py     # Error management
│   ├── user_management.py    # User operations
│   ├── lab_management.py     # Lab operations
│   ├── equipment_management.py   # Equipment operations
│   └── inventory_management.py   # Inventory operations
├── static/
│   └── images/              # Static assets
└── templates/
    ├── base.html           # Base template
    ├── dashboard.html      # Dashboard view
    ├── login.html          # Login page
    ├── profile.html        # User profile
    ├── labs/
    │   ├── view.html       # Lab listing
    │   ├── access.html     # Lab access
    │   ├── assignments.html # Lab assignments
    │   ├── confirm_booking.html
    │   └── mybookings.html # User bookings
    ├── equipment/
    │   ├── add.html        # Add equipment
    │   ├── check.html      # Check status
    │   ├── maintain.html   # Maintenance
    │   └── remove.html     # Remove equipment
    ├── inventory/
    │   ├── request.html    # Request form
    │   ├── purchase.html   # Purchase form
    │   └── status.html     # Request status
    └── maintenance/
        ├── reports.html    # Maintenance reports
        └── tasks.html      # Maintenance tasks
```

## Database Schema
- users: User information and authentication
- labs: Lab details and availability
- lab_bookings: Booking management
- equipment: Equipment tracking
- equipment_issues: Maintenance records
- equipment_requests: Usage requests
- equipment_removals: Removal tracking
- inventory_requests: New equipment requests
- purchase_requests: Purchase workflow
- it_staff_notifications: Staff alerts

## Setup

1. Clone the repository
```bash
git clone https://github.com/alaminerca/lab-management-system.git
cd lab-management-system
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python database/database_setup.py
```

5. Run the application
```bash
python app.py
```

## Test Users

### Administrator
- ID: 123
- Password: test123
- Permissions: Full system access

### Student
- ID: 456
- Password: test456
- Permissions: Lab booking, equipment requests

### Instructor
- ID: 321
- Password: test321
- Permissions: Lab booking and access

### IT Staff
- ID: 789
- Password: test789
- Permissions: Equipment maintenance and management

## Core Workflows

### Lab Booking Process
1. User selects available lab
2. Submits booking request with time slot
3. System verifies availability
4. Administrator approves/rejects
5. User gets access during booked slot

### Equipment Maintenance
1. Issue reported by user
2. IT staff notified
3. Maintenance task created
4. Resolution documented
5. Equipment status updated

### Inventory Management
1. User submits equipment request
2. System checks inventory
3. Purchase request created if needed
4. IT staff processes request
5. Equipment added to system

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
