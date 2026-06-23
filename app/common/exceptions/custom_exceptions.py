class AppBaseException(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class EntityNotFoundException(AppBaseException):
    """Raised when a requested resource is not found in the database."""
    def __init__(self, entity_name: str, entity_id: any):
        super().__init__(f"{entity_name} with ID {entity_id} not found", status_code=404)