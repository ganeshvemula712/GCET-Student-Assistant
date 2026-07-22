from enum import Enum


class UserSort(str, Enum):
    """
    Sorting options for users.
    """

    NEWEST = "newest"
    OLDEST = "oldest"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"