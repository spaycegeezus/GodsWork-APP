"""this is godswork.sql"""

# bcrypt for password hashing
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
# Fake user database (use a real one later)

    "zen": "peace2025",
    "fuck": "backdoor"
);
default_users = [
    ("Admin", "admin"),
    ("TestUser1", "pass123"),
    ("Dev", "devpass"),
    ("FuckPad", "X240"),
    ("Fuck", "BACKDOOR")
]
