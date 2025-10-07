from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import sqlite3
import os
from gw_screen.login import LoginScreen
from gw_screen.signup import SignupScreen
from gw_screen.task import TaskScreen
from gw_screen.service import ServiceScreen
# __init__.py

class GodScreenManager(ScreenManager):
    pass

# dev accounts for those who like the backdoor access
DEFAULT_USERS = [
    ("Admin", "admin"),
    ("TestUser1", "pass123"),
    ("Dev", "devpass"),
    ("FuckPad", "X240"),
    ("Fuck", "BACKDOOR")
]

def get_db_path():
    # absolute path based on gw_screen package folder
    base = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)  # make sure folder exists
    return os.path.join(data_dir, 'godswork.db')


def init_db():
    db_path = get_db_path()
    print(f"Using database at: {db_path}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance INTEGER DEFAULT 250000
        )
    ''')

    # add default users safely
    for user, pw in DEFAULT_USERS:
        c.execute(
            "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
            (user, pw)
        )

    conn.commit()
    conn.close()
    print("Database initialized with default accounts.")


class GodsWorkApp(App):
    init_db()
    def build(self):
        self.title = "God's Work"
        sm = GodScreenManager(transition=FadeTransition())

        for screen in [LoginScreen(name='login'),
                       SignupScreen(name='signup'),
                       TaskScreen(name='task'),
                       ServiceScreen(name='services')]:
            sm.add_widget(screen)

        return sm


if __name__ == '__main__':
    GodsWorkApp().run()
