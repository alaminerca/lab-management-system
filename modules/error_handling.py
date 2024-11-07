from typing import Optional, Dict, Any
import logging
from functools import wraps
import traceback

# Configure logging
logging.basicConfig(
    filename='lab_management.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LabManagementError(Exception):
    """Base exception class for Lab Management System"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(LabManagementError):
    """Raised when input validation fails"""
    pass

class DatabaseError(LabManagementError):
    """Raised when database operations fail"""
    pass

class AuthorizationError(LabManagementError):
    """Raised when user lacks required permissions"""
    pass

def handle_errors(func):
    """Decorator for consistent error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return {
                'success': True,
                'data': result,
                'error': None
            }
        except ValidationError as e:
            logging.warning(f"Validation error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': {
                    'code': e.error_code,
                    'message': str(e),
                    'type': 'validation'
                }
            }
        except DatabaseError as e:
            logging.error(f"Database error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': {
                    'code': e.error_code,
                    'message': str(e),
                    'type': 'database'
                }
            }
        except AuthorizationError as e:
            logging.warning(f"Authorization error: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': {
                    'code': e.error_code,
                    'message': str(e),
                    'type': 'authorization'
                }
            }
        except Exception as e:
            logging.critical(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return {
                'success': False,
                'data': None,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred',
                    'type': 'internal'
                }
            }
    return wrapper

class ErrorHandler:
    @staticmethod
    def validate_input(data: Dict, required_fields: list) -> None:
        """Validate input data"""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                'MISSING_FIELDS'
            )

    @staticmethod
    def check_authorization(user_id: int, required_permission: str) -> None:
        """Check if user has required permission"""
        from user_management import UserManager
        user = UserManager.get_user(user_id)
        if not user or required_permission not in user.get_permissions():
            raise AuthorizationError(
                "User lacks required permission",
                'UNAUTHORIZED'
            )

    @staticmethod
    def log_error(error: Exception, context: Optional[Dict] = None) -> None:
        """Log error with context"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        logging.error(f"Error occurred: {error_data}")