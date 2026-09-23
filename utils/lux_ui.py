"""
utils/lux_ui.py
Luxury UI primitives for the JOULES app.
Rounded / glowing / colourful replacements for stock Kivy widgets.
"""

from kivy.graphics import Color, Line, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

# ---------------------------------------------------------------------------
#  PALETTE  — tweak these to re-skin the whole app
# ---------------------------------------------------------------------------
GOLD       = [0.98, 0.78, 0.36, 1]
GOLD_DEEP  = [0.75, 0.53, 0.14, 1]
EMERALD    = [0.25, 0.85, 0.60, 1]
SAPPHIRE   = [0.34, 0.58, 0.98, 1]
AMETHYST   = [0.70, 0.46, 0.99, 1]
ROSE       = [0.98, 0.45, 0.60, 1]

INK_TOP    = [0.11, 0.10, 0.19, 1]     # backdrop gradient (top)
INK_BOTTOM = [0.03, 0.03, 0.07, 1]     # backdrop gradient (bottom)

CARD       = [1, 1, 1, 0.055]          # frosted card fill
CARD_EDGE  = [1, 1, 1, 0.10]
FIELD      = [1, 1, 1, 0.07]           # text field fill
FIELD_EDGE = [1, 1, 1, 0.16]

TEXT       = [0.96, 0.96, 1, 1]
TEXT_DIM   = [1, 1, 1, 0.55]


def vertical_gradient(top, bottom, size=(1, 256)):
    """
    Build a vertical gradient texture.
    Kivy Texture filters are `mag_filter` / `min_filter` (not magnification_filter).
    Using a taller strip (256 px) gives a smoother ramp than a 1x2.
    """
    tex = Texture.create(size=size, colorfmt='rgba')

    # Build the full column of pixels, bottom -> top
    w, h = size
    buf = bytearray()
    for y in range(h):
        t = y / (h - 1)              # 0 at bottom, 1 at top
        r = bottom[0] * (1 - t) + top[0] * t
        g = bottom[1] * (1 - t) + top[1] * t
        b = bottom[2] * (1 - t) + top[2] * t
        a = bottom[3] * (1 - t) + top[3] * t
        buf += bytes((int(r * 255), int(g * 255), int(b * 255), int(a * 255)))

    tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')

    # Kivy's actual attribute names:
    tex.mag_filter = 'linear'
    tex.min_filter = 'linear'
    tex.wrap = 'clamp_to_edge'
    return tex


# ---------------------------------------------------------------------------
#  ROUNDED BUTTON
# ---------------------------------------------------------------------------
class RoundedButton(Button):
    bg_color         = ListProperty(list(GOLD))
    bg_color_pressed = ListProperty(list(GOLD_DEEP))
    text_color       = ListProperty([0.06, 0.05, 0.10, 1])
    border_color     = ListProperty([1, 1, 1, 0.18])
    radius           = ListProperty([dp(18)] * 4)
    shadow_color     = ListProperty([0, 0, 0, 0.35])

    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('font_size', dp(15))
        super().__init__(**kwargs)
        self.bold = True

        with self.canvas.before:
            self._sh_c = Color(*self.shadow_color)
            self._sh_r = RoundedRectangle(radius=self.radius)
            self._bg_c = Color(*self.bg_color)
            self._bg_r = RoundedRectangle(radius=self.radius)
        with self.canvas.after:
            self._bd_c = Color(*self.border_color)
            self._bd_l = Line(width=1.1)

        self.bind(pos=self._refresh, size=self._refresh, state=self._refresh,
                  bg_color=self._refresh, bg_color_pressed=self._refresh,
                  border_color=self._refresh, radius=self._refresh,
                  shadow_color=self._refresh, text_color=self._refresh)
        self._refresh()

    def _refresh(self, *args):
        r = self.radius
        self._sh_c.rgba = self.shadow_color
        self._sh_r.pos = (self.x + dp(1), self.y - dp(3))
        self._sh_r.size = (max(self.width - dp(2), 0), self.height)
        self._sh_r.radius = r

        self._bg_c.rgba = (self.bg_color_pressed if self.state == 'down'
                           else self.bg_color)
        self._bg_r.pos = self.pos
        self._bg_r.size = self.size
        self._bg_r.radius = r

        self._bd_c.rgba = self.border_color
        self._bd_l.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, r[0])
        self.color = self.text_color


# ---------------------------------------------------------------------------
#  ROUNDED TEXT INPUT  (glows gold when focused)
# ---------------------------------------------------------------------------
class RoundedTextInput(TextInput):
    bg_color           = ListProperty(list(FIELD))
    border_color       = ListProperty(list(FIELD_EDGE))
    focus_border_color = ListProperty(list(GOLD))
    radius             = ListProperty([dp(14)] * 4)

    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_active', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('foreground_color', list(TEXT))
        kwargs.setdefault('cursor_color', list(GOLD))
        kwargs.setdefault('hint_text_color', [1, 1, 1, 0.35])
        kwargs.setdefault('selection_color', [0.98, 0.78, 0.36, 0.35])
        kwargs.setdefault('padding', [dp(14), dp(10)])
        kwargs.setdefault('font_size', dp(15))
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_c = Color(*self.bg_color)
            self._bg_r = RoundedRectangle(radius=self.radius)
            self._bd_c = Color(*self.border_color)
            self._bd_l = Line(width=1.3)

        self.bind(pos=self._refresh, size=self._refresh, focus=self._refresh,
                  bg_color=self._refresh, border_color=self._refresh,
                  radius=self._refresh)
        self._refresh()

    def _refresh(self, *args):
        r = self.radius
        self._bg_c.rgba = self.bg_color
        self._bg_r.pos = self.pos
        self._bg_r.size = self.size
        self._bg_r.radius = r

        self._bd_c.rgba = (self.focus_border_color if self.focus
                           else self.border_color)
        self._bd_l.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, r[0])


# ---------------------------------------------------------------------------
#  FROSTED CARD PANEL (auto-heights itself to its children)
# ---------------------------------------------------------------------------
class LuxCard(BoxLayout):
    bg_color     = ListProperty(list(CARD))
    border_color = ListProperty(list(CARD_EDGE))
    radius       = ListProperty([dp(22)] * 4)

    def __init__(self, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('padding', dp(16))
        kwargs.setdefault('spacing', dp(10))
        kwargs.setdefault('size_hint_y', None)
        super().__init__(**kwargs)

        with self.canvas.before:
            self._bg_c = Color(*self.bg_color)
            self._bg_r = RoundedRectangle(radius=self.radius)
            self._bd_c = Color(*self.border_color)
            self._bd_l = Line(width=1.0)

        self.bind(pos=self._refresh, size=self._refresh,
                  bg_color=self._refresh, border_color=self._refresh,
                  radius=self._refresh,
                  minimum_height=self.setter('height'))
        self._refresh()

    def _refresh(self, *args):
        r = self.radius
        self._bg_c.rgba = self.bg_color
        self._bg_r.pos = self.pos
        self._bg_r.size = self.size
        self._bg_r.radius = r

        self._bd_c.rgba = self.border_color
        self._bd_l.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, r[0])


class LuxDropDown(DropDown):
    """Dark rounded container that matches the lux theme."""
    def __init__(self, **kwargs):
        kwargs.setdefault('bar_width', dp(3))
        kwargs.setdefault('bar_color', list(GOLD))
        kwargs.setdefault('bar_inactive_color', list(FIELD_EDGE))
        kwargs.setdefault('background_color', (0, 0, 0, 0))   # we draw our own
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.09, 0.08, 0.15, 1)
            self._bg = RoundedRectangle(radius=[dp(12)] * 4)
            self._bd_c = Color(*CARD_EDGE)
            self._bd_l = Line(width=1.0)

        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bd_l.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, dp(12))

# ---------------------------------------------------------------------------
#  ROUNDED SPINNER (+ matching dropdown rows)
# ---------------------------------------------------------------------------
class LuxSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('color', list(TEXT))
        kwargs.setdefault('height', dp(44))
        kwargs.setdefault('font_size', dp(14))
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.13, 0.12, 0.21, 1)
            self._r = RoundedRectangle(radius=[dp(10)] * 4)

        self.bind(pos=self._sync, size=self._sync)
        self._sync()

    def _sync(self, *args):
        self._r.pos = (self.x + dp(4), self.y + dp(1))
        self._r.size = (max(self.width - dp(8), 0), self.height - dp(2))


class RoundedSpinner(Spinner):
    bg_color     = ListProperty(list(FIELD))
    border_color = ListProperty(list(FIELD_EDGE))
    radius       = ListProperty([dp(14)] * 4)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_disabled_normal', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('color', list(TEXT))
        kwargs.setdefault('font_size', dp(15))
        kwargs.setdefault('dropdown_cls', LuxDropDown)
        kwargs.setdefault('option_cls', LuxSpinnerOption)

        with self.canvas.before:
            self._bg_c = Color(*self.bg_color)
            self._bg_r = RoundedRectangle(radius=self.radius)
            self._bd_c = Color(*self.border_color)
            self._bd_l = Line(width=1.3)

        self.bind(pos=self._refresh, size=self._refresh, state=self._refresh,
                  bg_color=self._refresh, border_color=self._refresh,
                  radius=self._refresh)
        self._refresh()

    def _refresh(self, *args):
        r = self.radius
        self._bg_c.rgba = self.bg_color
        self._bg_r.pos = self.pos
        self._bg_r.size = self.size
        self._bg_r.radius = r

        self._bd_c.rgba = self.border_color
        self._bd_l.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, r[0])