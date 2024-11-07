from datetime import datetime
from typing import Optional, List
import sqlite3
import hashlib
from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, user_id: int, name: str, role: str, contact_info: str):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.contact_info = contact_info

    @abstractmethod
    def get_permissions(self) -> List[str]:
        pass

    def authenticate(self, password: str) -> bool:
        """Authenticate user with hashed password"""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        with sqlite3.connect('lab_management.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM users WHERE userID = ?",
                (self.user_id,)
            )
            result = cursor.fetchone()
            return result and result[0] == hashed


class Student(User):
    def __init__(self, user_id: int, name: str, contact_info: str, major: str):
        super().__init__(user_id, name, "student", contact_info)
        self.major = major

    def get_permissions(self) -> List[str]:
        return ["view_labs", "book_lab", "request_equipment"]

    def book_lab(self, lab_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Book a lab for a specific time slot"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_bookings (userID, labID, start_time, end_time)
                    VALUES (?, ?, ?, ?)
                """, (self.user_id, lab_id, start_time, end_time))
                return True
        except sqlite3.Error:
            return False


class Administrator(User):
    def get_permissions(self) -> List[str]:
        return ["all"]  # Administrators have full access

    def assign_lab(self, lab_id: str, user_id: int,
                   start_time: datetime, end_time: datetime) -> bool:
        """Assign a lab to a user"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lab_bookings (userID, labID, start_time, end_time, status)
                    VALUES (?, ?, ?, ?, 'approved')
                """, (user_id, lab_id, start_time, end_time))
                return True
        except sqlite3.Error:
            return False


class UserManager:
    @staticmethod
    def create_user(name: str, role: str, contact_info: str,
                    password: str, **kwargs) -> Optional[User]:
        """Create a new user in the system"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (name, role, contact_info, password_hash)
                    VALUES (?, ?, ?, ?)
                """, (name, role, contact_info, hashed_password))
                user_id = cursor.lastrowid

                if role == "student":
                    return Student(user_id, name, contact_info, kwargs.get('major', ''))
                elif role == "administrator":
                    return Administrator(user_id, name, contact_info)

                return None
        except sqlite3.Error:
            return None

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        """Retrieve a user from the database"""
        try:
            with sqlite3.connect('lab_management.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, role, contact_info FROM users WHERE userID = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                if result:
                    name, role, contact_info = result
                    if role == "student":
                        return Student(user_id, name, contact_info, "")
                    elif role == "administrator":
                        return Administrator(user_id, name, contact_info)
                return None
        except sqlite3.Error:
            return None