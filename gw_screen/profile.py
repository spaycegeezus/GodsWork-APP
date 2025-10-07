# this is profile.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from datetime import datetime
from utils.data_handler import DataHandler
from kivy.graphics import Rectangle
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id', 'default_user')
        super().__init__(**kwargs)

        self.data_handler = DataHandler()
        profile = self.data_handler.load_user_profile(self.user_id)

        self.username = profile.get("username", "Always Be Yourself. Semper Te Ate")
        self.bio = profile.get("bio", "You can edit this or it will stay this way")
        self.anonymize = profile.get("anonymize", False)
        self.profile_pic = profile.get("profile_pic", "LOGO.png")
        self.theme = profile.get("theme", {"bg_color": (1,1,1,1), "text_color": (0,0,0,1), "bg_image": "LogoBackground.jpg"})

        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=25, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.add_widget(self.scroll)

        with self.canvas.before:
            self.bg_image = Rectangle(source=self.theme.get("bg_image", "LogoBackground.jpg"), pos=self.pos, size=Window.size)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.build_view_mode()

        self.bio_input = TextInput(
            text=self.bio,
            multiline=True,
            size_hint=(1, None),
            height=100,
            background_color=(0, 0, 0, 0),  # fully transparent
            foreground_color=(1, 1, 1, 1),  # text color (white)
            padding=[10, 10, 10, 10]
        )

    def build_view_mode(self):
        self.layout.clear_widgets()

        # Profile picture
        self.layout.add_widget(Image(source=self.profile_pic, size_hint=(None, None), size=(150,150), pos_hint={'center_x':0.5}))

        # Labels
        self.username_label = Label(text=self.username, font_size=28, bold=True, color=self.theme["text_color"])
        self.layout.add_widget(self.username_label)
        self.bio_label = Label(text=self.bio, font_size=18, color=self.theme["text_color"])
        self.layout.add_widget(self.bio_label)

        # Buttons
        btn_config = [
            ('Edit Profile', (1,0.2,0.6,1), self.switch_to_edit_mode),
            ('Edit Theme', (0.7,0.7,0.2,1), self.open_theme_editor),
            ('Add a Service', (0.6,0.2,0.8,1), self.open_add_service_popup),
            ('View Services', (1,0.4,0.2,1), self.goto_service_directory),
            ('View Ledger', (0.2,0.6,1,1), self.goto_ledger),
            ('Back to Home', (0.1,0.8,0.2,1), self.go_home),
        ]
        for text, color, callback in btn_config:
            btn = Button(
                text=text,
                size_hint=(0.7, None),
                height=45,
                pos_hint={'center_x': 0.5},
                background_color=color,
                color=self.theme["text_color"]
            )
            btn.bind(on_press=callback)
            self.layout.add_widget(btn)

        anon_status = "Anonymous" if self.anonymize else "Visible"
        self.anon_label = Label(text=f'Privacy: {anon_status}', font_size=16, color=(0.85,0.85,0.85,1))
        self.layout.add_widget(self.anon_label)

    def _update_bg(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def open_theme_editor(self, instance):
        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)

        # Left side: inputs
        input_layout = BoxLayout(orientation='vertical', spacing=10)
        bg_color_input = TextInput(hint_text='BG Color (R,G,B)', text="0,1,0")
        text_color_input = TextInput(hint_text='Text Color (R,G,B)', text="1,1,1")

        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        save_btn = Button(text='Save Theme', background_color=(0.2, 0.6, 0.9, 1))
        back_btn = Button(text='Back', background_color=(0.8, 0.2, 0.2, 1))

        input_layout.add_widget(bg_color_input)
        input_layout.add_widget(text_color_input)
        input_layout.add_widget(button_layout)

        button_layout.add_widget(save_btn)
        button_layout.add_widget(back_btn)

        # Right side: color guide
        guide_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(0.4, 1))
        colors = [
            ("Red", (1, 0, 0)),
            ("Orange", (1, 0.5, 0)),
            ("Yellow", (1, 1, 0)),
            ("Green", (0, 1, 0)),
            ("Blue", (0, 0, 1)),
            ("Indigo", (0.29, 0, 0.51)),
            ("Violet", (0.56, 0, 1))
        ]
        for name, rgb in colors:
            label = Label(
                text=f"{name}  {rgb}",
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=30
            )
            label.canvas.before.add(Rectangle(size=(30, 30), pos=(0, 0)))  # Optional swatch
            guide_layout.add_widget(label)

        layout.add_widget(input_layout)
        layout.add_widget(guide_layout)

        # Create popup
        self.theme_popup = Popup(title="Edit Profile Theme", content=layout, size_hint=(0.9, 0.7))

        # Bind buttons
        save_btn.bind(on_press=lambda _: self.save_theme_and_close(
            bg_color_input.text, text_color_input.text
        ))
        back_btn.bind(on_press=lambda _: self.theme_popup.dismiss())

        self.theme_popup.open()

    def save_theme_and_close(self, bg_color, text_color, bg_image=None):
        self.theme = {
            "bg_color": tuple(map(float, bg_color.split(','))),
            "text_color": tuple(map(float, text_color.split(','))),
        }
        if bg_image:
            self.theme["bg_image"] = bg_image
        self.save_profile(None)
        if hasattr(self, 'theme_popup'):
            self.theme_popup.dismiss()    # Close popup after saving

    def switch_to_edit_mode(self, instance):
        self.layout.clear_widgets()

        self.username_input = TextInput(text=self.username, multiline=False) # top box in edit
        self.bio_input = TextInput(text=self.bio, multiline=True, size_hint=(1, None), height=120) # middle box in edit

        self.username_input = TextInput(
            text=self.bio,
            multiline=True,
            size_hint=(1, None),
            height=120,
            background_color=(1, 1, 1, 1),  # transparent
            foreground_color=(0,0,0),
            padding=[10, 10, 10, 10]
        )

        self.bio_input = TextInput(
            text=self.bio,
            multiline=True,
            size_hint=(1, None),
            height=120,
            background_color=(1, 1, 1, 1),  # transparent
            foreground_color=(0,0,0),
            padding=[10, 10, 10, 10]
        )

        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.bio_input)

        self.privacy_toggle = ToggleButton(
            text='ANON MODE: ON' if self.anonymize else 'ANON MODE: OFF',
            size_hint=(0.5,None), height=45, pos_hint={'center_x':0.5}
        )
        self.privacy_toggle.bind(on_press=self.toggle_anonymity)
        self.layout.add_widget(self.privacy_toggle)

        save_btn = Button(text='Save', size_hint=(0.5,None), height=45, pos_hint={'center_x':0.5})
        save_btn.bind(on_press=self.save_profile)
        self.layout.add_widget(save_btn)

    def toggle_anonymity(self, instance):
        self.anonymize = not self.anonymize
        self.anon_label.text = f'Privacy: {"Anonymous" if self.anonymize else "Visible"}'
        instance.text = 'ANON MODE: ON' if self.anonymize else 'ANON MODE: OFF'
        instance.background_color = (0.9, 0.2, 0.4, 1) if self.anonymize else (0.2, 0.7, 0.2, 1)
        self.user_id = hash(self.username) % 1000000 if self.anonymize else self.username

    def save_profile(self, instance):
        self.username = getattr(self, 'username_input', None) and self.username_input.text or self.username
        self.bio = getattr(self, 'bio_input', None) and self.bio_input.text or self.bio
        self.profile_pic = getattr(self, 'pic_input', None) and self.pic_input.text or self.profile_pic

        profile_data = {
            "username": self.username,
            "bio": self.bio,
            "anonymize": self.anonymize,
            "profile_pic": self.profile_pic,
            "theme": self.theme
        }
        self.data_handler.save_user_profile(self.user_id, profile_data)
        self.build_view_mode()

    def open_add_service_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        category_input = TextInput(hint_text='Service Category')
        description_input = TextInput(hint_text='Service Description')
        value_input = TextInput(hint_text='JOULE Value', input_filter='int')

        save_button = Button(text='Save', background_color=(0.2, 0.6, 0.9, 1), color=(1, 1, 1, 1))
        cancel_button = Button(text='Cancel', background_color=(0.9, 0.2, 0.4, 1), color=(1, 1, 1, 1))

        def save_service(_):
            service = {
                'timestamp': datetime.utcnow().isoformat(),
                'category': category_input.text.strip(),
                'description': description_input.text.strip(),
                'value': value_input.text.strip() or '0',
                'provider_id': self.user_id
            }
            handler = DataHandler()
            handler.save_service(service, self.user_id)
            popup.dismiss()

        save_button.bind(on_press=save_service)
        cancel_button.bind(on_press=lambda _: popup.dismiss())

        layout.add_widget(category_input)
        layout.add_widget(description_input)
        layout.add_widget(value_input)
        layout.add_widget(save_button)
        layout.add_widget(cancel_button)

        popup = Popup(title='Add a Service', content=layout, size_hint=(0.85, 0.7))
        popup.open()

    def goto_service_directory(self, instance):
        self.manager.current = 'service'

    def goto_ledger(self, instance):
        self.manager.current = 'ledger_viewer'

    def go_home(self, instance):
        self.manager.current = 'home'
