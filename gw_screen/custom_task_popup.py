# custom_task_popup.py

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class CustomTaskPopup(Popup):
    def __init__(self, on_submit, **kwargs):
        super().__init__(**kwargs)
        self.title = "Create Custom Task"
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = False
        self.on_submit = on_submit

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.category_input = TextInput(hint_text="Task Category", multiline=False)
        self.description_input = TextInput(hint_text="Task Description", multiline=False)
        self.value_input = TextInput(hint_text="Value (JOULES)", multiline=False, input_filter='int')
        self.weight_input = TextInput(hint_text="Enter Weight (kg)", multiline=False, input_filter='float')
        self.time_input = TextInput(hint_text="Enter Time (min)", multiline=False, input_filter='int')

        layout.add_widget(Label(text="Enter new task details:"))
        layout.add_widget(self.category_input)
        layout.add_widget(self.description_input)
        layout.add_widget(self.value_input)
        layout.add_widget(self.weight_input)
        layout.add_widget(self.time_input)

        btns = BoxLayout(size_hint_y=0.3)
        submit = Button(text="Submit")
        cancel = Button(text="Cancel")
        submit.bind(on_press=self.submit)
        cancel.bind(on_press=self.dismiss)
        btns.add_widget(submit)
        btns.add_widget(cancel)

        layout.add_widget(btns)
        self.add_widget(layout)

    def submit(self, instance):
        category = self.category_input.text.strip()
        description = self.description_input.text.strip()
        value_text = self.value_input.text.strip()
        weight_text = self.weight_input.text.strip()
        time_text = self.time_input.text.strip()

        if not category or not description or not value_text:
            self.show_error("All fields must be filled.")
            return

        try:
            value = int(value_text)
            weight = float(weight_text)
            time = int(time_text)
        except ValueError:
            self.show_error("Invalid number input. Please enter valid values for weight, time, and value.")
            return

        self.on_submit(category, description, value, weight, time)
        self.dismiss()

    def show_error(self, message):
        error_popup = Popup(
            title="Input Error",
            content=Label(text=message),
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )
        error_popup.open()
