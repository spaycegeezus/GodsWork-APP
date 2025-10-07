# this is home.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from gw_screen.profile import ProfileScreen
from gw_screen.task import TaskScreen
from gw_screen.service import ServiceScreen
from gw_screen.login import LoginScreen
from gw_screen.account import AccountScreen
from gw_screen.ledger_viewer import LedgerViewerScreen

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)
        self.build_view_mode()

        with self.canvas.before:
            self.bg_image = Rectangle(source='LogoBackground.jpg', pos=self.pos, size=Window.size)
        self.bind(size=self._update_bg, pos=self._update_bg)


    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def build_view_mode(self):
        self.layout.clear_widgets()

        logo = Image(source='LOGO.png', size_hint=(None, None), size=(180, 180), pos_hint={'center_x': 0.5}, allow_stretch=True, keep_ratio=True)
        self.layout.add_widget(logo)

        welcome_label = Label(text='Welcome to the ART Project', font_size=28, bold=True, size_hint=(1, None), height=40, halign='center', valign='middle', color=(1.0, 0.9, 0.4, 0.9))
        welcome_label.bind(size=welcome_label.setter('text_size'))
        self.layout.add_widget(welcome_label)

        subtitle = Label(text='A place of peace and productivity.\nPassion is Presence, thank you for showing up.', font_size=16, halign='center', valign='middle', size_hint=(1, None), height=60, color=(0.9, 0.9, 0.5, 0.4))
        subtitle.bind(size=subtitle.setter('text_size'))
        self.layout.add_widget(subtitle)

        profile_btn = Button(text='Profile', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5}, background_color=(0.2, 0.6, 0.4, 1), color=(1, 1, 1, 1), bold=True)
        profile_btn.bind(on_press=self.goto_profile)
        self.layout.add_widget(profile_btn)

        service_btn = Button(text='Service', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5}, background_color=(0.2, 0.6, 0.4, 1), color=(1, 1, 1, 1), bold=True)
        service_btn.bind(on_press=self.goto_service)
        self.layout.add_widget(service_btn)

        account_btn = Button(text='Account', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5}, background_color=(0.2, 0.8, 0.8, 1), color=(1, 1, 1, 1), bold=True)
        account_btn.bind(on_press=self.goto_account)
        self.layout.add_widget(account_btn)

        ledger_btn = Button(text='View Ledger', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5}, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), bold=True)
        ledger_btn.bind(on_press=self.goto_ledger)
        self.layout.add_widget(ledger_btn)

        ledger_btn = Button(text='Sign Out', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5}, background_color=(0.9, 0.1, 0.1, 1), color=(1, 1, 1, 1), bold=True)
        ledger_btn.bind(on_press=self.goto_login)
        self.layout.add_widget(ledger_btn)

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
        sm.add_widget(LoginScreen(name='logout'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(LedgerViewerScreen(name='ledger_viewer'))

        return sm


if __name__ == '__main__':
    HomeApp().run()
