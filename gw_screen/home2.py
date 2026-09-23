from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle
from kivy.core.window import Window

class NavButton(Button):
    """A consistently styled button for navigation."""
    def __init__(self, text, target_screen, bg_color=(0.2, 0.6, 0.4, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.target_screen = target_screen
        self.size_hint = (0.6, None)
        self.height = 40
        self.pos_hint = {'center_x': 0.5}
        self.background_color = bg_color
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.bind(on_press=self.go_to_screen)

    def go_to_screen(self, instance):
        # Access the screen manager through the parent chain
        screen = self.get_root_window().children[0]  # ScreenManager is root widget
        if isinstance(screen, ScreenManager):
            screen.transition.direction = 'left'  # consistent forward direction
            screen.current = self.target_screen
        else:
            # Fallback if not directly under ScreenManager (shouldn't happen)
            self.parent.parent.parent.manager.transition.direction = 'left'
            self.parent.parent.parent.manager.current = self.target_screen


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Background
        with self.canvas.before:
            self.bg_image = Rectangle(source='LogoBackground.jpg', pos=self.pos, size=Window.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Main layout inside a scroll view for responsiveness
        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15,
            size_hint_y=None
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)

        self.build_ui()

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def build_ui(self):
        """Create all widgets dynamically. Call again if data changes."""
        self.layout.clear_widgets()

        # Logo
        logo = Image(
            source='LOGO.png',
            size_hint=(None, None),
            size=(180, 180),
            pos_hint={'center_x': 0.5},
            allow_stretch=True,
            keep_ratio=True
        )
        self.layout.add_widget(logo)

        # Welcome text
        welcome_label = Label(
            text='Welcome to the ART Project',
            font_size=28,
            bold=True,
            size_hint=(1, None),
            height=40,
            halign='center',
            valign='middle',
            color=(1.0, 0.9, 0.4, 1)
        )
        welcome_label.bind(size=welcome_label.setter('text_size'))
        self.layout.add_widget(welcome_label)

        subtitle = Label(
            text='A place of peace and productivity.\nPassion is Presence, thank you for showing up.',
            font_size=16,
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=60,
            color=(0.9, 0.9, 0.5, 0.8)
        )
        subtitle.bind(size=subtitle.setter('text_size'))
        self.layout.add_widget(subtitle)

        # Navigation buttons with consistent styling and behavior
        self.layout.add_widget(NavButton(text='Profile', target_screen='profile', bg_color=(0.2, 0.6, 0.4, 1)))
        self.layout.add_widget(NavButton(text='Service', target_screen='service', bg_color=(0.2, 0.6, 0.4, 1)))
        self.layout.add_widget(NavButton(text='Account', target_screen='account', bg_color=(0.2, 0.8, 0.8, 1)))
        self.layout.add_widget(NavButton(text='View Ledger', target_screen='ledger_viewer', bg_color=(0.2, 0.5, 0.8, 1)))
        # Note: Task screen is not shown here, but you can add it if needed.
        self.layout.add_widget(NavButton(text='Sign Out', target_screen='login', bg_color=(0.9, 0.1, 0.1, 1)))
        self.layout.add_widget(NavButton(text='Tasks', target_screen='task', bg_color=(0.4, 0.4, 0.4, 1)))