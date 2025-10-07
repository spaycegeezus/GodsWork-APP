# this is login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from utils.security import verify_password
from utils.admin_vault import AdminVault
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_image = Rectangle(source='LogoBackground.jpg', pos=self.pos, size=self.size)

        self.bind(size=self._update_bg, pos=self._update_bg)

        layout.add_widget(Label(text="Login", font_size=40, size_hint=(1, 0.2)))

        self.username_input = TextInput(hint_text="Username", multiline=False)
        layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", multiline=False, password=True)
        layout.add_widget(self.password_input)

        self.message_label = Label(text="", font_size=14, size_hint=(1, 0.1), color=(1, 0, 0, 1))
        layout.add_widget(self.message_label)

        login_button = Button(text="Login", size_hint=(1, 0.3))
        login_button.bind(on_press=self.handle_login)
        layout.add_widget(login_button)

        # signup button
        signup_btn = Button(text='Sign UP', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5})
        signup_btn.bind(on_press=self.go_signup)
        layout.add_widget(signup_btn)

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def load_decrypted_pepper(self):
        """Securely load and decrypt the pepper using the AdminVault."""
        try:
            with open("data/encrypted_pepper.txt", "r") as f:
                encrypted_pepper = f.read().strip()

            if not encrypted_pepper:
                raise ValueError("Encrypted pepper is empty or invalid.")

            vault = AdminVault()
            if not (vault.unlock_layer(1, os.getenv("LAYER1_PASS")) and
                    vault.unlock_layer(2, os.getenv("LAYER2_PASS")) and
                    vault.unlock_layer(3, os.getenv("PEPPER_PASS"))):
                raise Exception("Admin vault unlock failed.")

            return vault.decrypt_layer(3, encrypted_pepper)

        except Exception as e:
            print(f"[Verification Error] {e}")
            return None

    def check_credentials(self, username, password):
        from gw_screen.__init__ import DEFAULT_USERS, get_db_path

        # Dev backdoor accounts
        for dev_user, dev_pass in DEFAULT_USERS:
            if username == dev_user and password == dev_pass:
                print(f"Dev backdoor login: {username}")
                return True

        # Normal user flow
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()

        if not row:
            self.message_label.text = "Username not found."
            return False

        stored_encrypted_hash = row[0]

        # Load pepper for normal users (optional, can be from env)
        pepper = os.getenv("PEPPER_SECRET", "default_pepper")

        # Verify password
        from utils.security import verify_password
        return verify_password(password, stored_encrypted_hash, username, pepper)

    def attempt_login(self, username, password):
        from gw_screen.__init__ import init_db
        init_db()

        # Backdoor dev accounts
        from gw_screen.__init__ import DEFAULT_USERS
        for dev_user, dev_pass in DEFAULT_USERS:
            if username == dev_user and password == dev_pass:
                print(f"Dev backdoor login: {username}")
                self.manager.current = 'home'
                return

        # Normal user flow
        if self.check_credentials(username, password):
            print(f"Welcome {username}!")
            self.manager.current = 'home'
        else:
            self.message_label.text = "Invalid username or password"
            print("Invalid login.")

    def handle_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.message_label.text = "Please enter both username and password."
            return

        if self.check_credentials(username, password):
            print(f"✅ Welcome {username}!")

            # Store the username globally for later screens
            if hasattr(self.manager, 'get_screen'):
                account_screen = self.manager.get_screen('account')
                if account_screen:
                    account_screen.current_username = username
                    account_screen.load_balance_from_username()
                    print(f"🔗 Passed username '{username}' to AccountScreen.")

            self.manager.current = 'home'
        else:
            self.message_label.text = "Invalid username or password"
            print("❌ Invalid login.")

    def go_signup(self, instance):
        from gw_screen.signup import SignupScreen
        self.manager.current = 'signup'