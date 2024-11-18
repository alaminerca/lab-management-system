from datetime import datetime
from typing import Optional, List, Dict
import sqlite3
from dataclasses import dataclass

@dataclass
class Lab:
    lab_id: str
    size: int
    location: str
    info: str
    is_available: bool
    created_at: datetime

class LabManagement:
    @staticmethod
    def create_lab(lab_id: str, size: int, location: str, info: str) -> bool:
        """Create a new lab in the system"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO labs (labID, size, location, info, isAvailable)
                    VALUES (?, ?, ?, ?, TRUE)
                """, (lab_id, size, location, info))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def get_all_labs() -> List[Lab]:
        """Get all labs from database"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT labID, size, location, info, isAvailable, created_at FROM labs')
                return [Lab(*row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []


    @staticmethod
    def get_lab(lab_id: str) -> Optional[Lab]:
        """Retrieve lab information"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM labs WHERE labID = ?",
                    (lab_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Lab(*result)
                return None
        except sqlite3.Error:
            return None

    @staticmethod
    def get_available_labs(start_time: datetime, end_time: datetime) -> List[Lab]:
        """Get list of available labs for a specific time slot"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.* FROM labs l
                    WHERE l.isAvailable = TRUE
                    AND l.labID NOT IN (
                        SELECT labID FROM lab_bookings
                        WHERE (start_time <= ? AND end_time >= ?)
                        OR (start_time <= ? AND end_time >= ?)
                        AND status != 'cancelled'
                    )
                """, (end_time, start_time, end_time, start_time))
                return [Lab(*row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    @staticmethod
    def is_lab_available(lab_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Check if a lab is available for a specific time slot"""
        try:
            print(f"Checking availability for lab {lab_id}")  # Debug print
            print(f"Time slot: {start_time} to {end_time}")  # Debug print

            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM lab_bookings
                    WHERE labID = ?
                    AND (
                        (start_time <= ? AND end_time >= ?)
                        OR (start_time <= ? AND end_time >= ?)
                    )
                    AND status != 'cancelled'
                """, (lab_id, end_time, start_time, end_time, start_time))
                count = cursor.fetchone()[0]
                print(f"Found {count} conflicting bookings")  # Debug print
                return count == 0
        except sqlite3.Error as e:
            print(f"Database error in is_lab_available: {e}")  # Debug print
            return False

    @staticmethod
    def book_lab(user_id: int, lab_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Book a lab for a specific time slot"""
        try:
            print(f"Attempting to book lab {lab_id}")  # Debug print
            print(f"User: {user_id}")  # Debug print
            print(f"Time: {start_time} to {end_time}")  # Debug print

            with sqlite3.connect('lab_management.db') as conn:
                # Check if lab is available
                if not LabManagement.is_lab_available(lab_id, start_time, end_time):
                    print("Lab not available")  # Debug print
                    return False

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_bookings (userID, labID, start_time, end_time, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (user_id, lab_id, start_time, end_time))
                print("Booking created successfully")  # Debug print
                return True
        except sqlite3.Error as e:
            print(f"Database error in book_lab: {e}")  # Debug print
            return False
    @staticmethod
    def get_lab_schedule(lab_id: str) -> List[Dict]:
        """Get the schedule for a specific lab"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT lb.*, u.name
                    FROM lab_bookings lb
                    JOIN users u ON lb.userID = u.userID
                    WHERE lb.labID = ?
                    AND lb.start_time >= datetime('now')
                    ORDER BY lb.start_time
                """, (lab_id,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    @staticmethod
    def get_user_bookings(user_id: int) -> List[Dict]:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        lb.bookingID,
                        lb.labID,
                        lb.start_time,
                        lb.end_time,
                        lb.status,
                        l.location,
                        l.info
                    FROM lab_bookings lb
                    JOIN labs l ON lb.labID = l.labID
                    WHERE lb.userID = ?
                    ORDER BY lb.start_time DESC
                """, (user_id,))
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def get_booking(booking_id: int) -> Optional[Dict]:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        lb.*,
                        l.location,
                        l.info
                    FROM lab_bookings lb
                    JOIN labs l ON lb.labID = l.labID
                    WHERE lb.bookingID = ?
                """, (booking_id,))
                columns = [description[0] for description in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def get_current_active_booking(user_id: int) -> Optional[Dict]:
        try:
            current_time = datetime.now()
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT bookingID, labID
                    FROM lab_bookings
                    WHERE userID = ?
                    AND status = 'approved'
                    AND start_time <= ?
                    AND end_time >= ?
                """, (user_id, current_time, current_time))
                result = cursor.fetchone()
                return {'booking_id': result[0], 'lab_id': result[1]} if result else None
        except sqlite3.Error:
            return None

    @staticmethod
    def update_booking_status(booking_id: int, action: str) -> bool:
        """Update booking status (approve/reject)"""
        try:
            status = 'approved' if action == 'approve' else 'rejected'
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE lab_bookings 
                    SET status = ? 
                    WHERE bookingID = ?
                """, (status, booking_id))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False


    @staticmethod
    def get_all_bookings() -> List[Dict]:
        """Get all bookings with user and lab details"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        lb.bookingID,
                        lb.userID,
                        lb.labID,
                        lb.start_time,
                        lb.end_time,
                        lb.status,
                        l.location,
                        l.size
                    FROM lab_bookings lb
                    JOIN labs l ON lb.labID = l.labID
                    ORDER BY lb.start_time DESC
                """)
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        return []