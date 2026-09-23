import tkinter as tk
from kivy.uix.screenmanager import Screen

class ProfileScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Profile Screen")
        label.pack()