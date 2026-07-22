from fastapi import HTTPException, status


class ConversationNotFoundException(HTTPException):
    """
    Raised when a conversation cannot be found.
    """

    def __init__(self, conversation_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found.",
        )


class DocumentNotFoundException(HTTPException):
    """
    Raised when a document cannot be found.
    """

    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{filename}' not found.",
        )


class DatabaseException(HTTPException):
    """
    Raised when a database operation fails.
    """

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed.",
        )

class UserAlreadyExistsException(HTTPException):

    def __init__(self):

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )
