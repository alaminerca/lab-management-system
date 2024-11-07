from datetime import datetime
from typing import Optional, List, Dict
import sqlite3
from dataclasses import dataclass


@dataclass
class Equipment:
    equip_id: int
    equip_type: str
    status: str
    last_checked: datetime


class EquipmentManagement:
    @staticmethod
    def add_equipment(equip_type: str) -> Optional[int]:
        """Add new equipment to the system"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO equipment (equipType, status, last_checked)
                    VALUES (?, 'operational', datetime('now'))
                """, (equip_type,))
                return cursor.lastrowid
        except sqlite3.Error:
            return None

    @staticmethod
    def request_equipment(user_id: int, equip_id: int) -> bool:
        """Request to use equipment"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                # Check if equipment is available
                cursor.execute("""
                    SELECT status FROM equipment 
                    WHERE equipID = ? AND status = 'operational'
                """, (equip_id,))

                if not cursor.fetchone():
                    return False

                cursor.execute("""
                    INSERT INTO equipment_requests (userID, equipID, status)
                    VALUES (?, ?, 'pending')
                """, (user_id, equip_id))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def approve_equipment_request(request_id: int) -> bool:
        """Approve an equipment request"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE equipment_requests
                    SET status = 'approved'
                    WHERE requestID = ?
                """, (request_id,))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def return_equipment(equip_id: int) -> bool:
        """Mark equipment as returned"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE equipment
                    SET status = 'operational', last_checked = datetime('now')
                    WHERE equipID = ?
                """, (equip_id,))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def get_equipment_history(equip_id: int) -> List[Dict]:
        """Get usage history for specific equipment"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT er.*, u.name as user_name
                    FROM equipment_requests er
                    JOIN users u ON er.userID = u.userID
                    WHERE er.equipID = ?
                    ORDER BY er.request_date DESC
                """, (equip_id,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    @staticmethod
    def schedule_maintenance(equip_id: int, maintenance_date: datetime) -> bool:
        """Schedule maintenance for equipment"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO maintenance_schedule (equipID, scheduled_date, status)
                    VALUES (?, ?, 'scheduled')
                """, (equip_id, maintenance_date))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def report_issue(equip_id: int, issue_description: str) -> bool:
        """Report an issue with equipment"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO equipment_issues (equipID, description, report_date)
                    VALUES (?, ?, datetime('now'))
                """, (equip_id, issue_description))

                # Update equipment status
                cursor.execute("""
                    UPDATE equipment
                    SET status = 'maintenance_required'
                    WHERE equipID = ?
                """, (equip_id,))
                return True
        except sqlite3.Error:
            return False