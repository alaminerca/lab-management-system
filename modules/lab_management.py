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
    def book_lab(user_id: int, lab_id: str,
                 start_time: datetime, end_time: datetime) -> bool:
        """Book a lab for a specific time slot"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                # Check if lab is available
                if not LabManagement.is_lab_available(lab_id, start_time, end_time):
                    return False

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_bookings (userID, labID, start_time, end_time)
                    VALUES (?, ?, ?, ?)
                """, (user_id, lab_id, start_time, end_time))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def is_lab_available(lab_id: str, start_time: datetime,
                        end_time: datetime) -> bool:
        """Check if a lab is available for a specific time slot"""
        try:
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
                return count == 0
        except sqlite3.Error:
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