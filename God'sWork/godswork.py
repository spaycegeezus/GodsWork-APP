import kivy.app
from kivy.uix.screenmanager import ScreenManager, Screen
from gw_screen.home import HomeScreen
from gw_screen.login import LoginScreen
from gw_screen.profile import ProfileScreen
import tkinter as tk


class GodScreenManager(ScreenManager):
    pass

class GodsWorkApp(App):
    def build(self):
        sm = GodScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == '__main__':
    GodsWorkApp().run()
