class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    pass

class UserCreationError(Exception):
    """Raised when user creation fails due to invalid data or database issues."""
    pass

class UserValidationError(Exception):
    """Raised when user data fails validation."""
    pass