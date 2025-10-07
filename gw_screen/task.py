# this is task.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from datetime import datetime
from kivy.uix.label import Label
from gw_screen.service_task_receipt import PaymentWindow
from utils.data_handler import DataHandler
from utils.ui_components import ServiceItem

class TaskScreen(Screen):
    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id', 'default_user')
        super().__init__(**kwargs)
        self.data_handler = DataHandler()

        # Layouts
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Top Buttons
        button_layout = BoxLayout(size_hint_y=None, height=50)
        add_task_button = Button(text='Add Task')
        add_task_button.bind(on_press=self.open_add_task_popup)
        button_layout.add_widget(add_task_button)

        home_button = Button(text='Home')
        home_button.bind(on_press=self.go_home)
        button_layout.add_widget(home_button)

        main_layout.add_widget(button_layout)

        # Task container
        self.task_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.task_container.bind(minimum_height=self.task_container.setter('height'))

        scroll_view = ScrollView()
        scroll_view.add_widget(self.task_container)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

        self.load_tasks()

    def load_tasks(self):
        self.task_container.clear_widgets()
        tasks = self.data_handler.load_tasks(self.user_id)

        for task in tasks:
            task_widget = ServiceItem(
                service_data=task,
                on_delete=self.delete_task,
                on_edit=self.assign_task
            )
            self.task_container.add_widget(task_widget)

    def open_add_task_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        description_input = TextInput(hint_text='Task Description')
        category_input = TextInput(hint_text='Category')
        value_input = TextInput(hint_text='Reward JOULES')

        save_button = Button(text='Save')
        cancel_button = Button(text='Cancel')

        def save_task(_):
            task = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'description': description_input.text,
                'category': category_input.text,
                'value': value_input.text or '0',
                'requester_id': self.user_id
            }
            self.data_handler.save_task(task, self.user_id)
            self.load_tasks()
            popup.dismiss()

        save_button.bind(on_press=save_task)
        cancel_button.bind(on_press=lambda _: popup.dismiss())

        layout.add_widget(description_input)
        layout.add_widget(category_input)
        layout.add_widget(value_input)
        layout.add_widget(save_button)
        layout.add_widget(cancel_button)

        popup = Popup(title='Add Task', content=layout, size_hint=(0.8, 0.7))
        popup.open()

    def assign_task(self, task_widget):
        task_data = task_widget.service_data
        requester_id = task_data.get('requester_id')
        recipient_id = self.user_id  # current user is accepting the task

        if requester_id == recipient_id:
            # Cannot accept own task
            popup = Popup(title="Invalid", content=Label(text="You cannot accept your own task."),
                          size_hint=(0.6, 0.3))
            popup.open()
            return

        def on_complete():
            self.load_tasks()

        payment_popup = PaymentWindow(
            user_id=requester_id,
            recipient_id=recipient_id,
            service_data=task_data,
            on_transaction_complete=on_complete
        )
        payment_popup.open()

    def delete_task(self, task_widget):
        from utils.data_handler import USER_FILE, ANON_FILE

        target_timestamp = task_widget.service_data.get('timestamp')
        tasks = self.data_handler.load_tasks(self.user_id)
        updated_tasks = [task for task in tasks if task.get('timestamp') != target_timestamp]

        data = self.data_handler._load_data(USER_FILE if self.user_id else ANON_FILE)

        if self.user_id:
            data[self.user_id]['tasks'] = updated_tasks
        else:
            data['tasks'] = updated_tasks

        self.data_handler._save_data(USER_FILE if self.user_id else ANON_FILE, data)

        # Remove only the widget, don't reload everything
        self.task_container.remove_widget(task_widget)

    def go_home(self, instance):
        self.manager.current = 'home'
