from kivy.uix.screenmanager import Screen
import tkinter as tk

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Login Screen")
        label.pack()