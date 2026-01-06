from enum import Enum

class Role(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"
