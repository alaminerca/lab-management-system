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
    @staticmethod
    @staticmethod
    def get_all_equipment() -> List[Dict]:
        """Retrieve all equipment with their status"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM equipment")
                rows = cursor.fetchall()  # Get rows once
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]  # Use stored rows
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def report_issue(equip_id: int, description: str, reported_by: int) -> bool:
        """Report equipment issue and update status"""
        try:
            print(f"Attempting to insert issue:")  # Debug prints
            print(f"Equipment ID: {equip_id}")
            print(f"Description: {description}")
            print(f"Reported by: {reported_by}")

            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                # Create issue record
                cursor.execute("""
                    INSERT INTO equipment_issues 
                    (equipID, description, reported_by, report_date)
                    VALUES (?, ?, ?, datetime('now'))
                """, (equip_id, description, reported_by))

                # Update equipment status
                cursor.execute("""
                    UPDATE equipment 
                    SET status = 'maintenance_required',
                        last_checked = datetime('now')
                    WHERE equipID = ?
                """, (equip_id,))

                conn.commit()  # Make sure to commit changes
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Print specific error
            return False

    @staticmethod
    def get_reported_issues() -> List[Dict]:
        """Get all reported and unresolved issues"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        ei.issueID,
                        e.equipID,
                        e.equipType,
                        ei.description as issue,
                        ei.report_date,
                        e.status
                    FROM equipment_issues ei
                    JOIN equipment e ON ei.equipID = e.equipID
                    WHERE ei.resolved_date IS NULL
                    ORDER BY ei.report_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Debug print
            return []

    @staticmethod
    def check_inventory(equip_type: str, quantity: int) -> Dict:
        """Simulate inventory check"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inventory_requests 
                    (equipment_type, quantity, request_date, status)
                    VALUES (?, ?, datetime('now'), 'pending')
                """, (equip_type, quantity))

                # Simulate inventory response (in real system, this would be an API call)
                is_available = True  # For testing, assume equipment is available

                return {
                    'available': is_available,
                    'request_id': cursor.lastrowid
                }
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {'available': False, 'error': str(e)}

    @staticmethod
    def get_inventory_requests(user_id: int) -> List[Dict]:
        """Get all inventory requests for admin"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM inventory_requests
                    ORDER BY request_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def get_pending_inventory_requests() -> List[Dict]:
        """Get pending requests from inventory"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM inventory_requests 
                    WHERE status = 'pending'
                    ORDER BY request_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def add_equipment_from_request(request_id: int) -> bool:
        """Add equipment from inventory request"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()

                # Get request details
                cursor.execute("SELECT equipment_type, quantity FROM inventory_requests WHERE request_id = ?",
                               (request_id,))
                request_data = cursor.fetchone()

                if not request_data:
                    return False

                equip_type, quantity = request_data

                # Add equipment
                for _ in range(quantity):
                    cursor.execute("""
                        INSERT INTO equipment (equipType, status, last_checked)
                        VALUES (?, 'operational', datetime('now'))
                    """, (equip_type,))

                # Update request status
                cursor.execute("""
                    UPDATE inventory_requests 
                    SET status = 'completed',
                        response_date = datetime('now')
                    WHERE request_id = ?
                """, (request_id,))

                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    @staticmethod
    def get_maintenance_tasks() -> List[Dict]:
        """Get all maintenance tasks with equipment details"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        ei.issueID,
                        e.equipID,
                        e.equipType,
                        ei.description as issue,
                        ei.report_date,
                        ei.resolved_date,
                        e.status,
                        ei.resolution
                    FROM equipment_issues ei
                    JOIN equipment e ON ei.equipID = e.equipID
                    ORDER BY ei.report_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def get_maintenance_task(task_id: int) -> Optional[Dict]:
        """Get specific maintenance task details"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        ei.issueID,
                        e.equipID,
                        e.equipType,
                        ei.description as issue,
                        ei.report_date,
                        e.status
                    FROM equipment_issues ei
                    JOIN equipment e ON ei.equipID = e.equipID
                    WHERE ei.issueID = ? AND ei.resolved_date IS NULL
                """, (task_id,))
                columns = [desc[0] for desc in cursor.description]
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def resolve_maintenance(task_id: int, resolution: str, staff_id: int) -> bool:
        """Complete maintenance task and update equipment status"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()

                # Get equipment ID for this task
                cursor.execute("SELECT equipID FROM equipment_issues WHERE issueID = ?",
                               (task_id,))
                equip_id = cursor.fetchone()[0]

                # Update issue status
                cursor.execute("""
                    UPDATE equipment_issues 
                    SET resolved_date = datetime('now'),
                        resolution = ?,
                        resolved_by = ?
                    WHERE issueID = ?
                """, (resolution, staff_id, task_id))

                # Update equipment status
                cursor.execute("""
                    UPDATE equipment 
                    SET status = 'operational',
                        last_checked = datetime('now')
                    WHERE equipID = ?
                """, (equip_id,))

                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False