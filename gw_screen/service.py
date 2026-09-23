# this is service.py

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from utils.data_handler import DataHandler
from utils.ui_components import ServiceItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from datetime import datetime
from gw_screen.service_task_receipt import PaymentWindow


class ServiceScreen(Screen):
    def __init__(self, **kwargs):
        self.user_id = kwargs.pop('user_id', 'default_user')
        super().__init__(**kwargs)
        self.data_handler = DataHandler()
        self.search_term = ""
        self.current_global_view = True

        self.main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.build_ui()
        self.add_widget(self.main_layout)

        # Initially load user-specific services
        self.load_services(global_view=True)

    def on_pre_enter(self, *args):
        from kivy.app import App
        app = App.get_running_app()
        if getattr(app, 'current_user', None):
            self.user_id = app.current_user
        self.load_services(global_view=self.current_global_view)

    def build_ui(self):
        self.search_input = TextInput(
            hint_text='Search services (category, description, provider)...',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        self.search_input.bind(text=self._on_search_change)
        self.main_layout.add_widget(self.search_input)

        # Button row
        button_layout = BoxLayout(size_hint_y=None, height=50)
        add_button = Button(text='Add Service')
        add_button.bind(on_press=self.open_add_service_popup)
        home_button = Button(text='Home')
        home_button.bind(on_press=self.go_home)

        self.view_toggle_button = ToggleButton(
            text='MY SERVICES', group='service_view',
            size_hint_x=None, width=220,
            height=50, background_normal='',
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1)
        )

        self.view_toggle_button.bind(on_press=self.toggle_view)

        view_hint = Label(
            text='Tap to switch between your services and the global service directory.',
            size_hint_y=None, height=25, font_size=12)

        button_layout.add_widget(add_button)
        button_layout.add_widget(home_button)
        button_layout.add_widget(self.view_toggle_button)
        self.main_layout.add_widget(button_layout)
        self.main_layout.add_widget(view_hint)

        # Scrollable service container
        self.service_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.service_container.bind(minimum_height=self.service_container.setter('height'))
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.service_container)
        self.main_layout.add_widget(scroll_view)

    def toggle_view(self, instance):
        self.load_services(global_view=not self.current_global_view)

    def load_services(self, global_view=True):
        self.current_global_view = global_view

        if hasattr(self, 'view_toggle_button'):
            if global_view:
                self.view_toggle_button.text = 'GLOBAL SERVICES'
                self.view_toggle_button.state = 'down'
            else:
                self.view_toggle_button.text = 'MY SERVICES'
                self.view_toggle_button.state = 'normal'

        self.service_container.clear_widgets()
        if global_view:
            services = self.data_handler.load_all_services()
        else:
            services = self.data_handler.load_services(user_id=self.user_id)

        # Apply search filter
        if self.search_term:
            needle = self.search_term.lower()
            services = [
                s for s in services
                if needle in str(s.get('category', '')).lower()
                   or needle in str(s.get('description', '')).lower()
                   or needle in str(s.get('provider_id', '')).lower()
            ]

        if not services:
            from kivy.uix.label import Label
            msg = "No matching services." if self.search_term else "No services available."
            self.service_container.add_widget(Label(
                text=msg, size_hint_y=None, height=40
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
        category_input = TextInput(hint_text='Service Category')
        description_input = TextInput(hint_text='Service Description')
        value_input = TextInput(hint_text='JOULE Value', input_filter='int')

        save_button = Button(text='Save')
        cancel_button = Button(text='Cancel')

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
            self.load_services(global_view=self.current_global_view)
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

    def _on_search_change(self, instance, value):
        self.search_term = value.strip()
        self.load_services(global_view=self.current_global_view)

    def _persist_edit_for_provider(self, updated):
        provider = updated.get('provider_id', self.user_id)
        services = self.data_handler.load_services(provider)
        for i, s in enumerate(services):
            if s == updated or (
                s.get('timestamp') == updated.get('timestamp')
                and s.get('provider_id') == provider
            ):
                services[i] = updated
                break
        self.data_handler.overwrite_services(services, provider)
        self.load_services(global_view=self.current_global_view)

    def edit_service(self, service_widget):
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
            self.load_services(global_view=self.current_global_view)
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

    def _remove_service_listing(self, service_data):
        """Remove a listing from its provider's profile after successful payment."""
        provider = service_data.get('provider_id')
        if not provider:
            return

        services = self.data_handler.load_services(provider)
        ts = service_data.get('timestamp')

        # Match by timestamp+provider — content may differ (last_edited, etc.)
        updated = [
            s for s in services
            if not (s.get('timestamp') == ts and s.get('provider_id') == provider)
        ]

        if len(updated) != len(services):
            self.data_handler.overwrite_services(updated, provider)
            print(f"Removed listing from {provider}: {service_data.get('category')}")
        else:
            print(f"Listing already gone (double-pay guard): {service_data.get('category')}")

    def delete_service(self, service_widget):
        target = service_widget.service_data
        ts = target.get('timestamp')
        target_provider = target.get('provider_id') or self.user_id

        def matches(s, provider):
            return (
                    s.get('timestamp') == ts
                    and (s.get('provider_id') or provider) == provider
            )

        # First try the provider from the widget
        services = self.data_handler.load_services(target_provider)
        updated = [s for s in services if not matches(s, target_provider)]

        if len(updated) != len(services):
            self.data_handler.overwrite_services(updated, target_provider)
            print(f"Deleted from provider file: {target_provider}")
        else:
            # Fallback: search all services to find the real provider
            all_services = self.data_handler.load_all_services()
            found_provider = None
            for s in all_services:
                if s.get('timestamp') == ts:
                    found_provider = s.get('provider_id') or target_provider
                    break

            if found_provider and found_provider != target_provider:
                services = self.data_handler.load_services(found_provider)
                updated = [s for s in services if not matches(s, found_provider)]
                if len(updated) != len(services):
                    self.data_handler.overwrite_services(updated, found_provider)
                    print(f"Deleted from fallback provider: {found_provider}")
                else:
                    print("Fallback found provider but no match in its file")
            else:
                print("Could not find service in any provider file")

        self.load_services(global_view=self.current_global_view)

    def pay_for_service(self, service_widget):
        service_data = service_widget.service_data
        recipient_id = service_data.get('provider_id', 'anonymous')

        def refresh_after_payment():
            # Remove the purchased listing so it can't be paid twice
            self._remove_service_listing(service_data)

            self.load_services(global_view=self.current_global_view)
            if 'account' in self.manager.screen_names:
                account_screen = self.manager.get_screen('account')
                account_screen.load_balance_from_username()

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
