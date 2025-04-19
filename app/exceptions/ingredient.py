class IngredientError(Exception):
    """Base class for ingredient exceptions."""
    pass

class IngredientCreationError(IngredientError):
    """Raised when ingredient creation fails for reasons other than existence."""
    pass

class IngredientAlreadyExistsError(IngredientError):
    """Raised when trying to create an ingredient that already exists."""
    pass

class IngredientRetrievalError(IngredientError):
    """Raised when fetching one or more ingredients fails."""
    pass

class IngredientSearchError(IngredientRetrievalError): # Can inherit if search is a form of retrieval
    """Raised when searching for ingredients fails."""
    pass

class IngredientUpdateError(IngredientError):
     """Raised when updating an ingredient fails."""
     pass

class IngredientDeletionError(IngredientError):
     """Raised when deleting an ingredient fails."""
     pass

class IngredientNotFoundError(IngredientRetrievalError):
     """Raised when a specific ingredient is not found."""
     pass