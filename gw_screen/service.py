# this is service.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from datetime import datetime
from utils.data_handler import DataHandler
from utils.ui_components import ServiceItem
from gw_screen.service_task_receipt import PaymentWindow

class ServiceScreen(Screen):
    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id', 'default_user')
        super().__init__(**kwargs)
        self.data_handler = DataHandler()

        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.build_ui()
        self.add_widget(self.main_layout)

        # Initially load user-specific services
        self.load_services(global_view=False)

    def on_pre_enter(self, *args):
        self.load_services(global_view=True)

    def build_ui(self):
        # Button row
        button_layout = BoxLayout(size_hint_y=None, height=50)
        add_button = Button(text='Add Service')
        add_button.bind(on_press=self.open_add_service_popup)
        home_button = Button(text='Home')
        home_button.bind(on_press=self.go_home)
        global_button = Button(text='Global View')
        global_button.bind(on_press=lambda x: self.load_services(global_view=True))

        button_layout.add_widget(add_button)
        button_layout.add_widget(home_button)
        button_layout.add_widget(global_button)
        self.main_layout.add_widget(button_layout)

        # Scrollable service container
        self.service_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.service_container.bind(minimum_height=self.service_container.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.service_container)
        self.main_layout.add_widget(scroll_view)

    def load_services(self, global_view=True):
        """Load services either user-specific or global."""
        self.service_container.clear_widgets()  # THIS IS CORRECT

        # Decide which data method to call
        if global_view:
            services = self.data_handler.load_all_services()
        else:
            services = self.data_handler.load_services(user_id=self.user_id)

        if not services:
            from kivy.uix.label import Label
            self.service_container.add_widget(Label(
                text="No services available.",
                size_hint_y=None,
                height=40
            ))
            return

        for service in services:
            item = ServiceItem(
                service_data=service,
                on_delete=self.delete_service,
                on_edit=self.pay_for_service
            )
            self.service_container.add_widget(item)

    def open_add_service_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        category_input = TextInput(hint_text='Category')
        description_input = TextInput(hint_text='Description')
        value_input = TextInput(hint_text='Service Value (JOULES)', input_filter='int')

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
            self.load_services(global_view=True)
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

    def delete_service(self, service_widget):
        """Delete a service for the correct user or anonymous"""
        services = self.data_handler.load_services(self.user_id)
        updated_services = [s for s in services if s != service_widget.service_data]
        self.data_handler.overwrite_services(updated_services, self.user_id)
        self.load_services(global_view=False)

    def pay_for_service(self, service_widget):
        service_data = service_widget.service_data
        recipient_id = service_data.get('provider_id', 'anonymous')

        def refresh_after_payment():
            self.load_services(global_view=True)
            if 'account' in self.manager.screen_names:
                account_screen = self.manager.get_screen('account')
                account_screen.update_balance_from_storage()

        popup = PaymentWindow(
            user_id=self.user_id,
            recipient_id=recipient_id,
            service_data=service_data,
            on_transaction_complete=refresh_after_payment
        )
        popup.open()

    def goto_service_directory(self, instance):
        self.manager.current = 'service'

    def go_home(self, instance):
        self.manager.current = 'home'
