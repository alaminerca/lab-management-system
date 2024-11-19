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
        """Get all inventory and purchase requests"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT equipment_type, quantity, request_date, status, NULL as justification
                    FROM inventory_requests
                    UNION ALL
                    SELECT equipment_type, quantity, request_date, status, justification
                    FROM purchase_requests
                    ORDER BY request_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def get_inventory_requests(user_id: int) -> List[Dict]:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                # Note the different ID column names
                cursor.execute("""
                    SELECT 'request' as type, request_id as id, equipment_type, quantity, request_date, status
                    FROM inventory_requests
                    UNION ALL
                    SELECT 'purchase' as type, purchase_id as id, equipment_type, quantity, request_date, status
                    FROM purchase_requests
                    ORDER BY request_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def get_pending_inventory_requests() -> List[Dict]:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        request_id, 
                        equipment_type, 
                        quantity, 
                        request_date,
                        'inventory' as source
                    FROM inventory_requests 
                    WHERE status = 'pending'
                    UNION ALL 
                    SELECT 
                        purchase_id, 
                        equipment_type, 
                        quantity, 
                        request_date,
                        'purchase' as source
                    FROM purchase_requests 
                    WHERE status = 'pending'
                    ORDER BY request_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                # Rename request_id to match template
                return rows
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    @staticmethod
    def add_equipment_from_request(request_id: int) -> bool:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                print(f"Processing request ID: {request_id}")  # Debug print

                # Check if already processed
                cursor.execute("""
                    SELECT equipment_type, quantity 
                    FROM (
                        SELECT request_id as id, equipment_type, quantity 
                        FROM inventory_requests 
                        WHERE status = 'pending'
                        UNION ALL
                        SELECT purchase_id as id, equipment_type, quantity 
                        FROM purchase_requests 
                        WHERE status = 'pending'
                    ) WHERE id = ?
                """, (request_id,))

                result = cursor.fetchone()
                print(f"Query result: {result}")  # Debug print

                if not result:
                    print("No pending request found")  # Debug print
                    return False

                equip_type, quantity = result
                print(f"Adding {quantity} {equip_type}(s)")  # Debug print

                # Add equipment
                for _ in range(quantity):
                    cursor.execute("""
                        INSERT INTO equipment (equipType, status, last_checked)
                        VALUES (?, 'operational', datetime('now'))
                    """, (equip_type,))

                # Update request status in both tables
                cursor.execute("""
                    UPDATE inventory_requests 
                    SET status = 'completed'
                    WHERE request_id = ? AND status = 'pending'
                """, (request_id,))

                cursor.execute("""
                    UPDATE purchase_requests 
                    SET status = 'completed'
                    WHERE purchase_id = ? AND status = 'pending'
                """, (request_id,))

                conn.commit()
                print("Transaction completed")  # Debug print
                return True

        except sqlite3.Error as e:
            print(f"Database error: {e}")  # Debug print
            return False

    @staticmethod
    def remove_equipment(equip_id: int, reason: str, staff_id: int) -> bool:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()

                # Check if equipment exists and is operational
                cursor.execute("SELECT status FROM equipment WHERE equipID = ?", (equip_id,))
                result = cursor.fetchone()
                if not result:
                    return False

                # Update equipment status to removed
                cursor.execute("""
                    UPDATE equipment 
                    SET status = 'removed',
                        last_checked = datetime('now')
                    WHERE equipID = ?
                """, (equip_id,))

                # Log removal
                cursor.execute("""
                    INSERT INTO equipment_removals 
                    (equipID, removed_by, removal_date, reason)
                    VALUES (?, ?, datetime('now'), ?)
                """, (equip_id, staff_id, reason))

                conn.commit()
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

    @staticmethod
    def submit_purchase_request(equip_type: str, quantity: int, justification: str, requester_id: int) -> bool:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO purchase_requests 
                    (equipment_type, quantity, justification, requester_id, status, request_date)
                    VALUES (?, ?, ?, ?, 'pending', datetime('now'))
                """, (equip_type, quantity, justification, requester_id))
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    @staticmethod
    def mark_purchase_delivered(request_id: int) -> bool:
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                # Update purchase request status
                cursor.execute("""
                    UPDATE purchase_requests 
                    SET status = 'delivered',
                        delivery_date = datetime('now')
                    WHERE request_id = ? AND status = 'pending'
                """, (request_id,))
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    @staticmethod
    def get_maintenance_history() -> List[Dict]:
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
                        ei.resolution,
                        e.status,
                        CASE 
                            WHEN ei.resolved_date IS NOT NULL THEN 'Resolved'
                            ELSE 'Pending'
                        END as maintenance_status
                    FROM equipment_issues ei
                    JOIN equipment e ON ei.equipID = e.equipID
                    ORDER BY ei.report_date DESC
                """)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []