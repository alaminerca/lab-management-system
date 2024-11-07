from datetime import datetime
from typing import Optional, Dict, List
import sqlite3


class InventoryManagement:
    @staticmethod
    def request_equipment(equipment_type: str, quantity: int) -> Dict:
        """Request equipment from inventory"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO equipment_requests 
                    (equipment_type, quantity, status, request_date)
                    VALUES (?, ?, 'pending', ?)
                """, (equipment_type, quantity, datetime.now()))

                request_id = cursor.lastrowid

                # Simulate inventory check (in real system, this would be an API call)
                is_available = True  # Simulated response

                return {
                    'success': True,
                    'request_id': request_id,
                    'status': 'available' if is_available else 'unavailable',
                    'message': f'Equipment {equipment_type} is {"" if is_available else "not "}available'
                }
        except sqlite3.Error as e:
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }

    @staticmethod
    def purchase_equipment(equipment_type: str, quantity: int) -> Dict:
        """Send purchase request to inventory system"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO purchase_requests 
                    (equipment_type, quantity, status, request_date)
                    VALUES (?, ?, 'pending', ?)
                """, (equipment_type, quantity, datetime.now()))

                purchase_id = cursor.lastrowid

                return {
                    'success': True,
                    'purchase_id': purchase_id,
                    'status': 'processing',
                    'message': 'Purchase request submitted successfully'
                }
        except sqlite3.Error as e:
            return {
                'success': False,
                'message': f'Database error: {str(e)}'
            }

    @staticmethod
    def notify_it_staff(request_id: int, equipment_details: Dict) -> bool:
        """Notify IT staff about new equipment"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO it_staff_notifications 
                    (request_id, equipment_details, status, notification_date)
                    VALUES (?, ?, 'pending', ?)
                """, (request_id, str(equipment_details), datetime.now()))
                return True
        except sqlite3.Error:
            return False

    @staticmethod
    def get_all_requests() -> List[Dict]:
        """Get all equipment requests and their status"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM equipment_requests 
                    UNION 
                    SELECT * FROM purchase_requests 
                    ORDER BY request_date DESC
                """)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    @staticmethod
    def get_it_notifications() -> List[Dict]:
        """Get pending IT staff notifications"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM it_staff_notifications 
                    WHERE status = 'pending' 
                    ORDER BY notification_date DESC
                """)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []