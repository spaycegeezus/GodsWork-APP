# this is home.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.graphics import RoundedRectangle, Color, Line, Rectangle
from kivy.core.window import Window
from kivy.properties import ListProperty
from kivy.metrics import dp

from gw_screen.profile import ProfileScreen
from gw_screen.task import TaskScreen
from gw_screen.service import ServiceScreen
from gw_screen.login import LoginScreen
from gw_screen.account import AccountScreen, AdminScreen
from utils.data_handler import DataHandler
from gw_screen.ledger_viewer import LedgerViewerScreen


class BubbleButton(Button):
    """
    Rounded ART-style button.

    Each button gets:
        - rounded/pill shape
        - individual accent color
        - subtle border
        - brighter pressed state
    """

    accent_color = ListProperty([0.2, 0.7, 0.7, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)

        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = 17

        # Draw our own button
        with self.canvas.before:
            self._button_color = Color(*self.accent_color)
            self._button_bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[(dp(24), dp(24))]
            )

        with self.canvas.after:
            self._border_color = Color(
                self.accent_color[0],
                self.accent_color[1],
                self.accent_color[2],
                0.95
            )
            self._border = Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(24)),
                width=1.3)

        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics,
            accent_color=self._update_graphics
        )

        self.bind(state=self._update_state)

    def _update_graphics(self, *args):
        self._button_color.rgb = self.accent_color[:3]
        self._button_color.a = self.accent_color[3]

        self._button_bg.pos = self.pos
        self._button_bg.size = self.size

        self._border_color.rgb = self.accent_color[:3]
        self._border_color.a = 0.95

        self._border.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            dp(24))

    def _update_state(self, *args):
        """Make the button visually respond when pressed."""

        if self.state == 'down':
            # Slightly darker while pressed
            self._button_color.rgba = (
                self.accent_color[0] * 0.78,
                self.accent_color[1] * 0.78,
                self.accent_color[2] * 0.78,
                self.accent_color[3]
            )

        else:
            self._button_color.rgba = self.accent_color

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        return super().on_touch_down(touch)


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data_handler = DataHandler()
        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(
            orientation='vertical',
            padding=(dp(10), dp(20), dp(10), dp(30)),
            spacing=dp(14),
            size_hint_y=None
        )

        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)

        self.build_view_mode()

        with self.canvas.before:
            self.bg_image = Rectangle(
                source='LogoBackground.jpg',
                pos=self.pos,
                size=Window.size
            )

        self.bind(
            size=self._update_bg,
            pos=self._update_bg
        )

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def build_view_mode(self):
        self.layout.clear_widgets()

        # ---------------------------------------------------------
        # LOGO
        # ---------------------------------------------------------

        logo = Image(
            source='LOGO.png',
            size_hint=(None, None),
            size=(dp(180), dp(180)),
            pos_hint={'center_x': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )

        self.layout.add_widget(logo)

        # ---------------------------------------------------------
        # WELCOME
        # ---------------------------------------------------------

        welcome_label = Label(
            text='Welcome to the ART Project',
            font_size=38,
            bold=True,
            size_hint=(1, None),
            height=dp(40),
            halign='center',
            valign='middle',
            color=(1.0, 0.9, 0.4, 0.95)
        )

        welcome_label.bind(size=welcome_label.setter('text_size'))
        self.layout.add_widget(welcome_label)
        subtitle = Label(
            text=(
                'A place of peace and productivity.\n'
                'Passion is Presence, thank you for showing up.'),
            font_size=20,
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(60),
            color=(0.9, 0.9, 0.5, 0.65)
        )

        subtitle.bind(size=subtitle.setter('text_size'))

        self.layout.add_widget(subtitle)

        # ---------------------------------------------------------
        # NAVIGATION BUTTONS
        # ---------------------------------------------------------

        profile_btn = BubbleButton(
            text='Profile',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.95, 0.60, 0.20, 1)
        )
        profile_btn.bind(on_press=self.goto_profile)
        self.layout.add_widget(profile_btn)

        service_btn = BubbleButton(
            text='Service',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.18, 0.72, 0.50, 1)
        )
        service_btn.bind(on_press=self.goto_service)
        self.layout.add_widget(service_btn)

        account_btn = BubbleButton(
            text='Account',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.12, 0.70, 0.82, 1)
        )
        account_btn.bind(on_press=self.goto_account)
        self.layout.add_widget(account_btn)

        ledger_btn = BubbleButton(
            text='View Ledger',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.40, 0.35, 0.82, 1)
        )
        ledger_btn.bind(on_press=self.goto_ledger)
        self.layout.add_widget(ledger_btn)

        # ---------------------------------------------------------
        # SIGN OUT
        # ---------------------------------------------------------

        signout_btn = BubbleButton(
            text='Sign Out',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.82, 0.25, 0.30, 1)
        )
        signout_btn.bind(on_press=self.goto_login)
        self.layout.add_widget(signout_btn)

        # ---------------------------------------------------------
        # ADMIN
        # ---------------------------------------------------------

        admin_btn = BubbleButton(
            text='Admin',
            size_hint=(0.6, None),
            height=dp(52),
            pos_hint={'center_x': 0.5},
            accent_color=(0.86, 0.25, 0.72, 1)
        )

        admin_btn.bind(on_press=self.goto_admin)
        # Hidden until we know the user is an administrator
        admin_btn.opacity = 0
        admin_btn.disabled = True

        self.layout.add_widget(admin_btn)
        self.admin_btn = admin_btn

    def on_pre_enter(self, *args):
        # Update admin button visibility
        if self.is_current_user_admin():
            self.admin_btn.opacity = 1
            self.admin_btn.disabled = False
        else:
            self.admin_btn.opacity = 0
            self.admin_btn.disabled = True

    def is_current_user_admin(self):
        account_screen = self.manager.get_screen('account')
        username = account_screen.current_username

        if not username:
            return False

        profile = self.data_handler.load_user_profile(username)

        return profile.get('admin', False)

    # ---------------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------------

    def goto_admin(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'admin'

    def goto_login(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'login'

    def goto_profile(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'profile'

    def goto_service(self, instance):
        self.manager.transition.direction = 'center'
        self.manager.current = 'service'

    def goto_task(self, instance):
        self.manager.transition.direction = 'top'
        self.manager.current = 'task'

    def goto_ledger(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = 'ledger_viewer'

    def goto_account(self, instance):
        self.manager.transition.direction = 'top'
        self.manager.current = 'account'

class HomeApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(ServiceScreen(name='service'))
        sm.add_widget(AdminScreen(name='admin'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(LedgerViewerScreen(name='ledger_viewer'))

        return sm

if __name__ == '__main__':
    HomeApp().run()