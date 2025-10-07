# this is add_service_popup.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from datetime import datetime
from utils.data_handler import DataHandler
from utils.ui_components import ServiceItem
from gw_screen.service import ServiceScreen

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
