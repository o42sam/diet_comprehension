class MealNotFoundError(Exception):
    """Raised when no meal is found for a user."""
    pass

class MealCreationError(Exception):
    """Raised when meal creation fails due to invalid data or database issues."""
    pass

class MealValidationError(Exception):
    """Raised when meal data fails validation."""
    pass