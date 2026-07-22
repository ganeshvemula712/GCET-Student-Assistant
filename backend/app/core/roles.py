from enum import Enum


class UserRole(str, Enum):
    """
    Application user roles.
    """
    STUDENT = "student"
    ADMIN = "admin"

    @classmethod
    def values(cls):
        return [role.value for role in cls]