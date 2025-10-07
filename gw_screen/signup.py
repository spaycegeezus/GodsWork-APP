import os
import sqlite3
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from utils.security import hash_password, encrypt_hash

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from gw_screen import __init__ as gw_init
        self.conn = sqlite3.connect(gw_init.get_db_path())
        self.cursor = self.conn.cursor()
        self.cursor = self.conn.cursor()
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_image = Rectangle(source='LogoBackground.jpg', pos=self.pos, size=self.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        layout.add_widget(Label(text="Sign Up", font_size=32, size_hint=(1, 0.2)))

        self.username_input = TextInput(hint_text="Username", multiline=False)
        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        self.password_confirm = TextInput(hint_text="Confirm Password", multiline=False, password=True)

        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.password_confirm)

        signup_button = Button(text="Sign Up", size_hint=(1, 0.3))
        signup_button.bind(on_press=self.handle_signup)
        layout.add_widget(signup_button)

        self.message_label = Label(text="", font_size=14, color=(1, 0, 0, 1), size_hint=(1, 0.1))
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def add_user(self, username, password):
        from gw_screen.__init__ import get_db_path
        import bcrypt
        from utils.admin_vault import AdminVault
        vault = AdminVault()
        if not (vault.unlock_layer(1, os.getenv("LAYER1_PASS")) and
                vault.unlock_layer(2, os.getenv("LAYER2_PASS")) and
                vault.unlock_layer(3, os.getenv("PEPPER_PASS"))):
            self.message_label.text = "Signup system error: vault unlock failed."
            return False
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        self.conn.commit()
        return True
        with open("data/encrypted_pepper.txt", "r") as f:
            encrypted_pepper = vault.encrypt_layer(3, some_pepper)
        pepper = vault.decrypt_layer(3, encrypted_pepper)

        try:
            encrypted = self.create_user(username, password, pepper)
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE NOT NULL,
                                password TEXT NOT NULL,
                                balance REAL DEFAULT 250000       
                            )
                        ''')
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, encrypted))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            self.message_label.text = "Username already exists."
        except Exception as e:
            self.message_label.text = f"Signup error: {e}"
        return False

    @staticmethod
    def create_user(username, password, pepper):
        raw_hash = hash_password(password)
        encrypted = encrypt_hash(raw_hash, username, pepper)
        return encrypted

    def handle_signup(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.password_confirm.text.strip()
        if self.add_user(username, password):
            self.manager.current = 'profile'
        if not username or not password:
            self.message_label.text = "Username and password required."
        elif password != confirm_password:
            self.message_label.text = "Passwords do not match."





