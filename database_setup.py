import sqlite3
from datetime import datetime

def setup_database():
    """Initialize the database with required tables"""
    with sqlite3.connect('lab_management.db') as conn:
        cursor = conn.cursor()

        # Create Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            contact_info TEXT,
            password_hash TEXT NOT NULL,
            major TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create Labs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS labs (
            labID TEXT PRIMARY KEY,
            size INTEGER,
            location TEXT,
            info TEXT,
            isAvailable BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create Equipment table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            equipID INTEGER PRIMARY KEY AUTOINCREMENT,
            equipType TEXT NOT NULL,
            status TEXT DEFAULT 'operational',
            last_checked DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create Lab Bookings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_bookings (
            bookingID INTEGER PRIMARY KEY AUTOINCREMENT,
            userID INTEGER,
            labID TEXT,
            start_time DATETIME,
            end_time DATETIME,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userID) REFERENCES users(userID),
            FOREIGN KEY (labID) REFERENCES labs(labID)
        )
        """)

        # Create Equipment Requests table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_requests (
            requestID INTEGER PRIMARY KEY AUTOINCREMENT,
            userID INTEGER,
            equipID INTEGER,
            request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            return_date DATETIME,
            FOREIGN KEY (userID) REFERENCES users(userID),
            FOREIGN KEY (equipID) REFERENCES equipment(equipID)
        )
        """)

        # Create Maintenance Schedule table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance_schedule (
            scheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            equipID INTEGER,
            scheduled_date DATETIME,
            status TEXT DEFAULT 'scheduled',
            completed_date DATETIME,
            notes TEXT,
            FOREIGN KEY (equipID) REFERENCES equipment(equipID)
        )
        """)

        # Create Equipment Issues table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipment_issues (
            issueID INTEGER PRIMARY KEY AUTOINCREMENT,
            equipID INTEGER,
            description TEXT,
            report_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_date DATETIME,
            resolution_notes TEXT,
            FOREIGN KEY (equipID) REFERENCES equipment(equipID)
        )
        """)

def insert_sample_data():
    """Insert sample data for testing"""
    with sqlite3.connect('lab_management.db') as conn:
        cursor = conn.cursor()

        # Sample Users
        cursor.executemany("""
        INSERT INTO users (name, role, contact_info, password_hash, major)
        VALUES (?, ?, ?, ?, ?)
        """, [
            ('Admin User', 'administrator', 'admin@lab.com', 'hashed_password', None),
            ('John Student', 'student', 'john@student.com', 'hashed_password', 'Computer Science'),
            ('IT Staff', 'staff', 'it@lab.com', 'hashed_password', None)
        ])

        # Sample Labs
        cursor.executemany("""
        INSERT INTO labs (labID, size, location, info)
        VALUES (?, ?, ?, ?)
        """, [
            ('LAB001', 30, 'Building A, Floor 1', 'General Purpose Lab'),
            ('LAB002', 25, 'Building A, Floor 2', 'Programming Lab'),
            ('LAB003', 20, 'Building B, Floor 1', 'Hardware Lab')
        ])

        # Sample Equipment
        cursor.executemany("""
        INSERT INTO equipment (equipType, status, last_checked)
        VALUES (?, ?, ?)
        """, [
            ('Computer', 'operational', datetime.now().isoformat()),
            ('Printer', 'operational', datetime.now().isoformat()),
            ('Scanner', 'maintenance_required', datetime.now().isoformat())
        ])

if __name__ == '__main__':
    setup_database()
    insert_sample_data()
    print("Database setup completed successfully!")