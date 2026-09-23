# this is login.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, NumericProperty
from utils.security import verify_password
from utils.admin_vault import AdminVault
import sqlite3
import os
from dotenv import load_dotenv
from kivy.core.window import Window
from kivy.metrics import dp


load_dotenv()


class RoundedButton(Button):
    """A Button whose background is a rounded rectangle."""

    bg_color = ListProperty([0.15, 0.55, 0.95, 1])       # normal
    bg_color_down = ListProperty([0.10, 0.40, 0.75, 1])  # pressed
    radius = ListProperty([dp(14)])          # ✅ ListProperty, not NumericProperty

    def __init__(self, **kwargs):
        # Remove Kivy's default rectangular background
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_color_instruction = Color(*self.bg_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self.radius,
            )

        # Keep the rectangle synced with the widget
        self.bind(
            pos=self._update_bg,
            size=self._update_bg,
            radius=self._update_bg,
            bg_color=self._update_bg_color,
            state=self._on_state,
        )

    def _update_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = self.radius

    def _update_bg_color(self, *args):
        if self.state == 'normal':
            self._bg_color_instruction.rgba = self.bg_color

    def _on_state(self, instance, value):
        if value == 'down':
            self._bg_color_instruction.rgba = self.bg_color_down
        else:
            self._bg_color_instruction.rgba = self.bg_color

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # FloatLayout gives us precise control over where the login card sits
        root = FloatLayout()

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 1)
            self.bg_image = Rectangle(
                source='LogoBackground.jpg',
                pos=self.pos,
                size=self.size
            )

        self.bind(size=self._update_bg, pos=self._update_bg)

        # ---------------------------------------------------------
        # LOGIN FORM
        # ---------------------------------------------------------
        # Height is determined ONLY by its contents.
        self.form = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=dp(360),
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(15),
            pos_hint={
                'center_x': 0.5,
                'top': 0.92
            }
        )

        # Critical: form grows only as large as its contents
        self.form.bind(
            minimum_height=self.form.setter('height')
        )

        # Title
        self.form.add_widget(Label(
            text="Login",
            font_size=dp(32),
            size_hint_y=None,
            height=dp(60)
        ))

        # Username
        self.username_input = TextInput(
            hint_text="Username",
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(50)
        )
        self.form.add_widget(self.username_input)

        # Password
        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            write_tab=False,
            password=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.form.add_widget(self.password_input)

        # Message
        self.message_label = Label(
            text="",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24),
            color=(1, 0, 0, 1)
        )
        self.form.add_widget(self.message_label)

        login_button = RoundedButton(
            text="Login",
            size_hint_y=None,
            height=dp(56),
            radius=[dp(14)],
            bg_color=[0.90, 0.55, 0.62, 1],
            bg_color_down=[0.55, 0.35, 0.40, 1],
        )
        login_button.bind(on_press=self.handle_login)
        self.form.add_widget(login_button)

        signup_btn = RoundedButton(
            text='Sign UP',
            size_hint_y=None,
            height=dp(56),
            radius=[dp(14)],
            bg_color=[0.90, 0.55, 0.62, 1],
            bg_color_down=[0.55, 0.35, 0.40, 1],
        )
        signup_btn.bind(on_press=self.go_signup)
        self.form.add_widget(signup_btn)

        root.add_widget(self.form)
        self.add_widget(root)

        # ---------------------------------------------------------
        # KEYBOARD FLOW
        # ---------------------------------------------------------
        self.username_input.bind(
            on_text_validate=lambda *_:
            setattr(self.password_input, 'focus', True)
        )

        self.password_input.bind(
            on_text_validate=self.handle_login
        )

        # ---------------------------------------------------------
        # RESPONSIVE WINDOW HANDLING
        # ---------------------------------------------------------
        Window.bind(size=self._apply_responsive)
        self._apply_responsive()

    def _apply_responsive(self, *args):
        """Pick card width based on window shape. Re-runs on resize."""
        w, h = Window.size
        portrait = h >= w

        if portrait:
            # Phone portrait: nearly full width, capped by screen
            card_width = min(w * 0.9, dp(420))
            card_height_hint = 0.6
        else:
            # Desktop / landscape: narrower card, taller proportion
            card_width = min(w * 0.4, dp(460))
            card_height_hint = 0.75

        self.form.width = card_width
        self.form.size_hint_y = card_height_hint

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def _propagate_user(self, username):
        """Push the logged-in username to every screen that cares."""
        from kivy.app import App
        app = App.get_running_app()
        app.current_user = username  # single source of truth

        sm = self.manager
        for name in sm.screen_names:
            screen = sm.get_screen(name)
            if hasattr(screen, 'user_id'):
                screen.user_id = username
            if hasattr(screen, 'current_username'):
                screen.current_username = username

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
            print(f"Welcome {username} you are now logged in!")
            self._propagate_user(username)

            # keep the existing account screen call if you want the balance to load immediately
            account_screen = self.manager.get_screen('account')
            account_screen.current_username = username
            account_screen.load_balance_from_username()

            self.manager.current = 'home'

            # Store the username globally for later screens
            if hasattr(self.manager, 'get_screen'):
                account_screen = self.manager.get_screen('account')
                if account_screen:
                    account_screen.current_username = username
                    account_screen.load_balance_from_username()
                    print(f" Passed username '{username}' to AccountScreen for global use by other screen systems.")
        else:
            self.message_label.text = "Invalid username or password"
            print("Invalid login.")

    def go_signup(self, instance):
        from gw_screen.signup import SignupScreen
        self.manager.current = 'signup'