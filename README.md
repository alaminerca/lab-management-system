# Lab Management System

A comprehensive system for managing computer labs, equipment, and resources in an educational institution.

## Features

- Lab booking and management
- Equipment tracking and maintenance
- Role-based access control (Admin, Student, IT Staff)
- Inventory management

## Setup

1. Clone the repository
```bash
git clone [repository-url]
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
python database/schema_updates.sql
```

5. Run the application
```bash
python app.py
```

## Project Structure
```
lab_management_system/
├── app.py
├── database/
│   └── schema_updates.sql
├── modules/
│   ├── __init__.py
│   ├── error_handling.py
│   ├── user_management.py
│   ├── lab_management.py
│   ├── equipment_management.py
│   └── inventory_management.py
└── templates/
    ├── base.html
    ├── login.html
    └── dashboard.html
```

## Test Users

- Administrator: ID: 123, Password: test123
- Student: ID: 456, Password: test456
- IT Staff: ID: 789, Password: test789

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
