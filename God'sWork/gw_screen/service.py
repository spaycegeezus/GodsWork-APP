from kivy.uix.screenmanager import Screen
import tkinter as tk

class ServiceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Service Screen")
        label.pack()