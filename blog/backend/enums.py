import enum


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"
    UNREGISTERED = "unregistered"
