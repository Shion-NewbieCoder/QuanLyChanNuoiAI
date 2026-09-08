"""Presentation choices for locally bundled animal illustrations."""

AVATAR_CHOICES = (
    ("", "Tự động theo loại vật nuôi"),
    ("cow", "Bò"),
    ("pig", "Heo / Lợn"),
    ("goat", "Dê"),
    ("sheep", "Cừu"),
    ("buffalo", "Trâu"),
    ("herd", "Đàn vật nuôi"),
    ("animal", "Hình đại diện chung"),
)
AVATAR_NAMES = frozenset(name for name, _ in AVATAR_CHOICES if name)
