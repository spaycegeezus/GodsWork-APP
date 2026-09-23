# profile.py

import os
from datetime import datetime
from kivy.core.window import Window
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle

from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton

from utils.data_handler import DataHandler


# ================================================================
# LOCAL IMAGE CONFIGURATION
# ================================================================

DEFAULT_PROFILE_IMAGE = "LOGO.png"
DEFAULT_BACKGROUND_IMAGE = "LogoBackground.jpg"


# ================================================================
# HELPERS
# ================================================================

def resolve_local_image(path, fallback):
    """
    Return the selected local image if it still exists.

    If the saved path is empty, invalid, or the file was moved/deleted,
    automatically use the default ART image.
    """
    if path:
        try:
            if os.path.isfile(path):
                return path
        except (TypeError, ValueError, OSError):
            pass

    return fallback


def parse_rgba(value, default=(1, 1, 1, 1)):

    try:
        parts = [
            float(part.strip())
            for part in value.split(",")
            if part.strip()
        ]

        if len(parts) == 3:
            parts.append(1.0)

        if len(parts) != 4:
            return default

        return tuple( max(0.0, min(1.0, value)) for value in parts)

    except (ValueError, TypeError):
        return default

def rgba_to_string(value):
    """
    Convert an RGBA tuple/list into editable text.
    """
    return ",".join(
        str(round(float(component), 3))
        for component in value
    )

# ================================================================
# ELEGANT BUTTON
# ================================================================

class ElegantButton(Button):
    """
    Reusable rounded ART-style button.
    """
    accent_color = ListProperty([0.3, 0.6, 0.9, 1])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Remove Kivy's default rectangular button texture.
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.font_size = dp(16)
        self.bold = True
        self.color = (1, 1, 1, 1)

        with self.canvas.before:

            self._bg_color = Color(*self.accent_color)

            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[(dp(22), dp(22)),])

        with self.canvas.after:
            self._border_color = Color(
                self.accent_color[0],
                self.accent_color[1],
                self.accent_color[2], 0.95)

            self._border = Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(22)),
                width=1.2)

        self.bind(
            pos=self._update_graphics,
            size=self._update_graphics,
            accent_color=self._update_graphics,
            state=self._update_state
        )

    def _update_graphics(self, *args):

        self._bg_color.rgba = self.accent_color

        self._bg.pos = self.pos
        self._bg.size = self.size

        self._border_color.rgba = (
            self.accent_color[0],
            self.accent_color[1],
            self.accent_color[2], 0.95)

        self._border.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            dp(22))

    def _update_state(self, *args):

        if self.state == "down":

            self._bg_color.rgba = (
                min(self.accent_color[0] * 0.78, 1),
                min(self.accent_color[1] * 0.78, 1),
                min(self.accent_color[2] * 0.78, 1),
                self.accent_color[3]
            )

        else:

            self._bg_color.rgba = self.accent_color


# ================================================================
# PROFILE SCREEN
# ================================================================

class ProfileScreen(Screen):

    def __init__(self, **kwargs):

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # Keep the original local profile ID.
        # Anonymity changes visibility, not the database record.
        # ---------------------------------------------------------

        self.user_id = kwargs.pop(
            "user_id",
            "default_user"
        )
        super().__init__(**kwargs)
        self.data_handler = DataHandler()
        profile = self.data_handler.load_user_profile(
            self.user_id
        ) or {}

        # ---------------------------------------------------------
        # BASIC PROFILE
        # ---------------------------------------------------------

        self.username = profile.get(
            "username",
            "Always Be Yourself. Semper Te Ate"
        )

        self.bio = profile.get(
            "bio",
            "You can edit this or it will stay this way"
        )

        self.anonymize = bool(
            profile.get("anonymize", False))

        # ---------------------------------------------------------
        # LOCAL PROFILE IMAGE
        # ---------------------------------------------------------

        stored_profile_pic = profile.get(
            "profile_pic",
            DEFAULT_PROFILE_IMAGE
        )

        self.profile_pic = resolve_local_image(
            stored_profile_pic,
            DEFAULT_PROFILE_IMAGE
        )

        # ---------------------------------------------------------
        # THEME
        # ---------------------------------------------------------

        default_theme = {
            "bg_color": [1, 1, 1, 1],
            "text_color": [1, 1, 1, 1],
            "bg_image": DEFAULT_BACKGROUND_IMAGE
        }

        stored_theme = profile.get(
            "theme",
            {}
        )

        if not isinstance(
            stored_theme,
            dict
        ):
            stored_theme = {}

        self.theme = {
            "bg_color": parse_rgba(
                rgba_to_string(
                    stored_theme.get(
                        "bg_color",
                        default_theme["bg_color"]
                    )
                ),
                default=tuple(
                    default_theme["bg_color"]
                )
            ),

            "text_color": parse_rgba(
                rgba_to_string(
                    stored_theme.get(
                        "text_color",
                        default_theme["text_color"]
                    )
                ),
                default=tuple(
                    default_theme["text_color"]
                )
            ),

            "bg_image": resolve_local_image(
                stored_theme.get(
                    "bg_image",
                    DEFAULT_BACKGROUND_IMAGE
                ),
                DEFAULT_BACKGROUND_IMAGE
            )
        }

        # =========================================================
        # MAIN SCROLL AREA
        # =========================================================

        self.scroll = ScrollView(
            size_hint=(1, 1)
        )

        self.layout = BoxLayout(
            orientation="vertical",
            padding=[
                dp(25),
                dp(30),
                dp(25),
                dp(35)
            ],
            spacing=dp(18),
            size_hint_y=None
        )

        self.layout.bind(
            minimum_height=
            self.layout.setter("height")
        )

        self.scroll.add_widget(
            self.layout
        )

        self.add_widget(
            self.scroll
        )

        # =========================================================
        # BACKGROUND
        # =========================================================

        # Background color layer.
        with self.canvas.before:

            self.bg_color_instruction = Color(
                *self.theme["bg_color"]
            )

            self.bg_color_rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

            # Background image layer.
            self.bg_image = Rectangle(
                source=self.theme["bg_image"],
                pos=self.pos,
                size=self.size
            )

        self.bind(
            size=self._update_bg,
            pos=self._update_bg
        )

        # =========================================================
        # INITIAL VIEW
        # =========================================================

        self.build_view_mode()

    # =============================================================
    # BACKGROUND
    # =============================================================

    def _update_bg(self, *args):

        self.bg_color_rect.pos = self.pos
        self.bg_color_rect.size = self.size

        self.bg_image.pos = self.pos
        self.bg_image.size = self.size

    def refresh_background(self):

        """
        Re-check the local background path and safely fall back
        to the ART default when necessary.
        """

        configured_path = self.theme.get(
            "bg_image",
            DEFAULT_BACKGROUND_IMAGE
        )

        resolved_path = resolve_local_image(
            configured_path,
            DEFAULT_BACKGROUND_IMAGE
        )

        self.theme["bg_image"] = resolved_path

        self.bg_color_instruction.rgba = (
            self.theme["bg_color"]
        )

        self.bg_image.source = resolved_path

        self.bg_image.pos = self.pos
        self.bg_image.size = self.size

        # Reload texture when needed.
        try:
            self.bg_image.texture_update()
        except Exception:
            pass

    # =============================================================
    # VIEW MODE
    # =============================================================

    def build_view_mode(self):

        self.layout.clear_widgets()

        self.refresh_background()

        # ---------------------------------------------------------
        # PROFILE PICTURE
        # ---------------------------------------------------------

        self.profile_pic = resolve_local_image(
            self.profile_pic,
            DEFAULT_PROFILE_IMAGE
        )

        profile_image = Image(
            source=self.profile_pic,
            size_hint=(None, None),
            size=(dp(150), dp(150)),
            pos_hint={"center_x": 0.5},
            allow_stretch=True,
            keep_ratio=True
        )

        self.layout.add_widget(
            profile_image
        )

        # ---------------------------------------------------------
        # USERNAME
        # ---------------------------------------------------------

        display_name = ("Anonymous User" if self.anonymize else self.username)

        self.username_label = Label(
            text=display_name,
            font_size=dp(28),
            bold=True,
            color=self.theme["text_color"],
            size_hint=(1, None),
            height=dp(48),
            halign="center",
            valign="middle"
        )

        self.username_label.bind(size=self.username_label.setter("text_size"))
        self.layout.add_widget(self.username_label)

        # ---------------------------------------------------------
        # BIO
        # ---------------------------------------------------------

        bio_display = (
            "This profile is currently anonymous."
            if self.anonymize
            else self.bio
        )

        self.bio_label = Label(
            text=bio_display,
            font_size=dp(18),
            color=self.theme["text_color"],
            size_hint=(1, None),
            height=dp(80),
            halign="center",
            valign="middle"
        )

        self.bio_label.bind(size=self.bio_label.setter("text_size"))
        self.layout.add_widget(self.bio_label)

        # ---------------------------------------------------------
        # LOCAL PROFILE STATUS
        # ---------------------------------------------------------

        local_status = Label(
            text="LOCAL PROFILE • Images stay on this device",
            font_size=dp(13),
            color=(0.80, 0.90, 0.85, 1),
            size_hint=(1, None),
            height=dp(30),
            halign="center",
            valign="middle")

        local_status.bind(size=local_status.setter("text_size"))
        self.layout.add_widget(local_status)

        # ---------------------------------------------------------
        # BUTTONS
        # ---------------------------------------------------------

        btn_config = [
            ("Edit Profile", (1.0, 0.20, 0.60, 1), self.switch_to_edit_mode),
            ("Customize Appearance", (0.70, 0.70, 0.20, 1), self.open_theme_editor),
            ("Add a Service", (0.60, 0.20, 0.80, 1), self.open_add_service_popup),
            ("View Services", (1.0, 0.40, 0.20, 1), self.goto_service_directory),
            ("View Ledger", (0.20, 0.60, 1.0, 1), self.goto_ledger),
            ("Back to Home", (0.10, 0.80, 0.20, 1), self.go_home),]

        for text, color, callback in btn_config:

            btn = ElegantButton(
                text=text,
                size_hint=(0.70, None),
                height=dp(54),
                pos_hint={"center_x": 0.5},
                accent_color=color,
                color=self.theme["text_color"])

            btn.bind(on_press=callback)
            self.layout.add_widget(btn)

        # ---------------------------------------------------------
        # PRIVACY STATUS
        # ---------------------------------------------------------

        anon_status = ("Anonymous" if self.anonymize else "Visible")

        self.anon_label = Label(
            text=f"Privacy: {anon_status}",
            font_size=dp(16),
            color=(0.85, 0.85, 0.85, 1),
            size_hint=(1, None),
            height=dp(34),
            halign="center",
            valign="middle")

        self.anon_label.bind(size=self.anon_label.setter( "text_size"))
        self.layout.add_widget(self.anon_label)

    # =============================================================
    # THEME EDITOR
    # =============================================================

    def open_theme_editor(self, instance):
        root = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(14))
        # ---------------------------------------------------------
        # IMAGE PREVIEW
        # ---------------------------------------------------------

        preview = Image(
            source=resolve_local_image(self.theme.get("bg_image"), DEFAULT_BACKGROUND_IMAGE),
            size_hint=(1, None),
            height=dp(170),
            allow_stretch=True,
            keep_ratio=True)

        root.add_widget(preview)

        # ---------------------------------------------------------
        # BACKGROUND IMAGE PATH DISPLAY
        # ---------------------------------------------------------

        image_status = Label(text=self._friendly_path(self.theme.get("bg_image")),
            size_hint=(1, None),
            height=dp(40),
            font_size=dp(12),
            halign="center",
            valign="middle")

        image_status.bind(size=image_status.setter("text_size"))
        root.add_widget(image_status)

        # ---------------------------------------------------------
        # IMAGE BUTTONS
        # ---------------------------------------------------------

        image_buttons = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(54),
            spacing=dp(10))

        choose_bg_button = ElegantButton(
            text="Choose Background",
            accent_color=(0.35, 0.55, 0.90, 1))

        reset_bg_button = ElegantButton(
            text="Use ART Default",
            accent_color=(0.55, 0.55, 0.55, 1))

        image_buttons.add_widget(choose_bg_button)
        image_buttons.add_widget(reset_bg_button)
        root.add_widget(image_buttons)

        # ---------------------------------------------------------
        # TEXT COLOR
        # ---------------------------------------------------------

        text_color_label = Label(
            text="Text Color (R,G,B,A)",
            size_hint=(1, None),
            height=dp(30),
            halign="left",
            valign="middle"
        )

        text_color_label.bind(size=text_color_label.setter("text_size"))
        root.add_widget(text_color_label)
        text_color_input = TextInput(
            text=rgba_to_string(self.theme["text_color"]),
            multiline=False,
            size_hint=(1, None),
            height=dp(48))

        root.add_widget(text_color_input)

        # ---------------------------------------------------------
        # BACKGROUND COLOR
        # ---------------------------------------------------------

        bg_color_label = Label(
            text="Background Tint (R,G,B,A)",
            size_hint=(1, None),
            height=dp(30),
            halign="left",
            valign="middle"
        )

        bg_color_label.bind(size=bg_color_label.setter("text_size"))

        root.add_widget(bg_color_label)

        bg_color_input = TextInput(
            text=rgba_to_string(self.theme["bg_color"]),
            multiline=False,
            size_hint=(1, None),
            height=dp(48))

        root.add_widget(bg_color_input)

        # ---------------------------------------------------------
        # COLOR GUIDE
        # ---------------------------------------------------------

        guide = Label(
            text=(
                "Examples:\n"
                "Red = 1,0,0,1\n"
                "Green = 0,1,0,1\n"
                "Blue = 0,0,1,1\n"
                "White = 1,1,1,1\n"
                "Black = 0,0,0,1"
            ),
            size_hint=(1, None),
            height=dp(110),
            halign="center",
            valign="middle"
        )

        guide.bind(size=guide.setter("text_size"))
        root.add_widget(guide)

        # ---------------------------------------------------------
        # SAVE / CANCEL
        # ---------------------------------------------------------

        button_layout = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(58),
            spacing=dp(10)
        )

        save_button = ElegantButton(
            text="Save Appearance",
            accent_color=(0.20, 0.60, 0.90, 1))

        cancel_button = ElegantButton(
            text="Cancel",
            accent_color=(0.80, 0.20, 0.20, 1))

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)
        root.add_widget(button_layout)

        # ---------------------------------------------------------
        # POPUP
        # ---------------------------------------------------------

        self.theme_popup = Popup(
            title="Customize Local Profile",
            content=root,
            size_hint=(0.93, 0.90)
        )

        # ---------------------------------------------------------
        # CALLBACKS
        # ---------------------------------------------------------

        def choose_background(_):

            self.open_image_picker(
                title="Choose Background Image",
                callback=lambda selected:
                self._set_background_preview(selected, preview, image_status))

        def reset_background(_):

            self.theme["bg_image"] = (DEFAULT_BACKGROUND_IMAGE)
            preview.source = (DEFAULT_BACKGROUND_IMAGE)
            image_status.text = ("Using ART default background")

        def save_theme(_):

            new_text_color = parse_rgba(
                text_color_input.text,
                default=self.theme["text_color"]
            )

            new_bg_color = parse_rgba(
                bg_color_input.text,
                default=self.theme["bg_color"])

            self.save_theme_and_close(
                bg_color=new_bg_color,
                text_color=new_text_color,
                bg_image=self.theme.get("bg_image", DEFAULT_BACKGROUND_IMAGE))

        choose_bg_button.bind(on_press=choose_background)
        reset_bg_button.bind(on_press=reset_background)
        save_button.bind(on_press=save_theme)
        cancel_button.bind(on_press=lambda _: self.theme_popup.dismiss())

        self.theme_popup.open()

    # =============================================================
    # IMAGE PICKER
    # =============================================================

    def open_image_picker(self, title, callback):

        root = BoxLayout( orientation="vertical", spacing=dp(10), padding=dp(10) )

        chooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=[
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.webp",
                "*.gif"
            ],
            multiselect=False
        )

        root.add_widget(chooser)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(58),
            spacing=dp(10))

        select_button = ElegantButton(
            text="Use Selected Image",
            accent_color=(0.20, 0.65, 0.40, 1))

        cancel_button = ElegantButton(
            text="Cancel",
            accent_color=(0.80, 0.20, 0.20, 1))

        buttons.add_widget(select_button)
        buttons.add_widget(cancel_button)
        root.add_widget(buttons)

        popup = Popup(title=title, content=root, size_hint=(0.95, 0.90))

        def select_image(_):
            if not chooser.selection:
                return
            selected = chooser.selection[0]
            if not os.path.isfile(selected):
                return
            callback(selected)

            popup.dismiss()

        select_button.bind(on_press=select_image)
        cancel_button.bind(on_press=lambda _: popup.dismiss())

        popup.open()

    # =============================================================
    # IMAGE PREVIEW
    # =============================================================

    def _set_background_preview( self, selected_path, preview, status_label):

        resolved = resolve_local_image(selected_path, DEFAULT_BACKGROUND_IMAGE)
        self.theme["bg_image"] = resolved
        preview.source = resolved
        status_label.text = (self._friendly_path(resolved))

        try:
            preview.reload()
        except Exception:
            pass

    # =============================================================
    # FRIENDLY LOCAL PATH
    # =============================================================

    def _friendly_path(self, path):

        if not path:
            return "Using ART default"

        if path == DEFAULT_BACKGROUND_IMAGE:
            return "Using ART default background"

        expanded = os.path.expanduser(
            str(path)
        )

        if len(expanded) > 70:
            return ("…" + expanded[-67:])

        return expanded

    # =============================================================
    # SAVE THEME
    # =============================================================

    def save_theme_and_close(self, bg_color, text_color, bg_image=None):

        # Preserve existing values instead of replacing
        # the entire theme dictionary.

        self.theme["bg_color"] = tuple(bg_color)
        self.theme["text_color"] = tuple(text_color)
        if bg_image:
            self.theme["bg_image"] = (resolve_local_image(bg_image, DEFAULT_BACKGROUND_IMAGE))
        else:
            self.theme["bg_image"] = (DEFAULT_BACKGROUND_IMAGE)

        self.save_profile(None)

        if hasattr(self, "theme_popup"):
            self.theme_popup.dismiss()

    # =============================================================
    # PROFILE EDIT MODE
    # =============================================================

    def switch_to_edit_mode(self, instance):
        self.layout.clear_widgets()
        # ---------------------------------------------------------
        # PROFILE IMAGE
        # ---------------------------------------------------------

        current_picture = resolve_local_image(self.profile_pic, DEFAULT_PROFILE_IMAGE)

        profile_preview = Image(
            source=current_picture, size_hint=(None, None),
            size=(dp(130), dp(130)), pos_hint={"center_x": 0.5})

        self.layout.add_widget(profile_preview)

        # ---------------------------------------------------------
        # CHANGE PROFILE PICTURE
        # ---------------------------------------------------------

        choose_picture_button = ElegantButton(
            text="Choose Profile Picture",
            size_hint=(0.70, None),
            height=dp(52),
            pos_hint={"center_x": 0.5},
            accent_color=( 0.55, 0.30, 0.90, 1))

        reset_picture_button = ElegantButton(
            text="Use ART Logo",
            size_hint=(0.70, None),
            height=dp(52),
            pos_hint={"center_x": 0.5},
            accent_color=(0.50, 0.50, 0.50, 1))

        self.layout.add_widget(choose_picture_button)
        self.layout.add_widget(reset_picture_button)

        # ---------------------------------------------------------
        # USERNAME
        # ---------------------------------------------------------

        self.username_input = TextInput(
            text=self.username,
            multiline=False,
            size_hint=(1, None),
            height=dp(52),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)])

        self.layout.add_widget(self.username_input)

        # ---------------------------------------------------------
        # BIO
        # ---------------------------------------------------------

        self.bio_input = TextInput(
            text=self.bio,
            multiline=True,
            size_hint=(1, None),
            height=dp(120),
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[dp(10), dp(10), dp(10), dp(10)])

        self.layout.add_widget(self.bio_input)

        # ---------------------------------------------------------
        # PRIVACY TOGGLE
        # ---------------------------------------------------------

        self.privacy_toggle = ToggleButton(
            text=("ANON MODE: ON"
                if self.anonymize
                else "ANON MODE: OFF"
            ),

            size_hint=(0.50, None),
            height=dp(52),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_down="",
            background_color=(
                (0.90, 0.20, 0.40, 1)
                if self.anonymize
                else (0.20, 0.70, 0.20, 1)
            ),
            color=(1, 1, 1, 1),
            bold=True)

        self.privacy_toggle.bind(on_press=self.toggle_anonymity)
        self.layout.add_widget(self.privacy_toggle)

        # ---------------------------------------------------------
        # SAVE
        # ---------------------------------------------------------

        save_btn = ElegantButton(
            text="Save Profile",
            size_hint=(0.50, None),
            height=dp(54),
            pos_hint={"center_x": 0.5},
            accent_color=(0.20, 0.70, 0.40, 1),
            color=(1, 1, 1, 1))

        save_btn.bind(on_press=self.save_profile)
        self.layout.add_widget(save_btn)

        # ---------------------------------------------------------
        # BACK
        # ---------------------------------------------------------

        back_btn = ElegantButton(
            text="Cancel",
            size_hint=(0.50, None),
            height=dp(54),
            pos_hint={"center_x": 0.5},
            accent_color=(0.70, 0.25, 0.25, 1))

        back_btn.bind(on_press=lambda _: self.build_view_mode())
        self.layout.add_widget(back_btn)

        # ---------------------------------------------------------
        # IMAGE CALLBACKS
        # ---------------------------------------------------------

        def choose_picture(_):
            self.open_image_picker(
                title="Choose Profile Picture",
                callback=lambda selected:
                self._set_profile_picture_preview(selected, profile_preview))

        def reset_picture(_):
            self.profile_pic = (DEFAULT_PROFILE_IMAGE)
            profile_preview.source = (DEFAULT_PROFILE_IMAGE)

            try:
                profile_preview.reload()
            except Exception:
                pass

        choose_picture_button.bind(on_press=choose_picture)
        reset_picture_button.bind(on_press=reset_picture)

    # =============================================================
    # PROFILE IMAGE PREVIEW
    # =============================================================

    def _set_profile_picture_preview(self, selected_path, preview):

        resolved = resolve_local_image(selected_path, DEFAULT_PROFILE_IMAGE)
        self.profile_pic = resolved
        preview.source = resolved

        try:
            preview.reload()
        except Exception:
            pass

    # =============================================================
    # PRIVACY
    # =============================================================

    def toggle_anonymity(self, instance):

        self.anonymize = not self.anonymize

        instance.text = ("ANON MODE: ON"
            if self.anonymize
            else "ANON MODE: OFF")

        instance.background_color = ((0.90, 0.20, 0.40, 1)
            if self.anonymize
            else (0.20, 0.70, 0.20, 1))

    # =============================================================
    # SAVE PROFILE
    # =============================================================

    def save_profile(self, instance):

        # ---------------------------------------------------------
        # USERNAME
        # ---------------------------------------------------------

        if hasattr(self, "username_input"):
            new_username = (self.username_input.text.strip())
            if new_username:
                self.username = new_username

        # ---------------------------------------------------------
        # BIO
        # ---------------------------------------------------------

        if hasattr(self, "bio_input"):
            self.bio = self.bio_input.text

        # ---------------------------------------------------------
        # PROFILE IMAGE
        # ---------------------------------------------------------

        self.profile_pic = resolve_local_image(self.profile_pic, DEFAULT_PROFILE_IMAGE)

        # ---------------------------------------------------------
        # BACKGROUND IMAGE
        # ---------------------------------------------------------

        self.theme["bg_image"] = (resolve_local_image(
            self.theme.get("bg_image"), DEFAULT_BACKGROUND_IMAGE))

        # ---------------------------------------------------------
        # PROFILE DATA
        # ---------------------------------------------------------

        profile_data = {
            "username": self.username,
            "bio": self.bio,
            "anonymize": self.anonymize,
            "profile_pic": self.profile_pic,
            "theme": {"bg_color": list(self.theme["bg_color"]),
                "text_color": list(self.theme["text_color"]),
                "bg_image": self.theme["bg_image"]}}

        # ---------------------------------------------------------
        # SAVE TO EXISTING DATA HANDLER
        # ---------------------------------------------------------

        self.data_handler.save_user_profile(self.user_id, profile_data)

        # ---------------------------------------------------------
        # REFRESH SCREEN
        # ---------------------------------------------------------

        self.build_view_mode()

    # =============================================================
    # ADD SERVICE POPUP
    # =============================================================

    def open_add_service_popup(self, instance):

        layout = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        category_input = TextInput(hint_text="Service Category")
        description_input = TextInput(hint_text="Service Description")
        value_input = TextInput(hint_text="JOULE Value", input_filter="int")
        save_button = ElegantButton(
            text="Save",
            size_hint_y=None,
            height=dp(54),
            accent_color=(0.20, 0.60, 0.90, 1),
            color=(1, 1, 1, 1))

        cancel_button = ElegantButton(
            text="Cancel",
            size_hint_y=None,
            height=dp(54),
            accent_color=(0.90, 0.20, 0.40, 1),
            color=(1, 1, 1, 1))

        def save_service(_):

            service = {
                "timestamp":
                    datetime.utcnow().isoformat(),
                "category":
                    category_input.text.strip(),
                "description":
                    description_input.text.strip(),
                "value":
                    value_input.text.strip() or "0",
                "provider_id":
                    self.user_id
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

        popup = Popup(title="Add a Service", content=layout, size_hint=(0.85, 0.70))
        popup.open()

    # =============================================================
    # NAVIGATION
    # =============================================================

    def goto_service_directory(self, instance):
        self.manager.current = "service"

    def goto_ledger(self, instance):
        self.manager.current = "ledger_viewer"

    def go_home(self, instance):
        self.manager.current = "home"