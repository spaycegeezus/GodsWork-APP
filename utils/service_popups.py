# utils/service_popups.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from datetime import datetime


def open_service_popup(screen, service_data=None, on_saved=None, provider_id=None):
    """Add or edit a service. Field set matches DataHandler.save_service's schema.

    service_data=None  -> add mode (creates new service)
    service_data=dict  -> edit mode (updates in place, preserves timestamp/provider_id)
    provider_id        -> who the service belongs to. Falls back to screen.user_id,
                          then 'anonymous'.
    """
    is_edit = service_data is not None
    service_data = service_data or {}

    if provider_id is None:
        provider_id = getattr(screen, 'user_id', None) or 'anonymous'

    layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

    category_input = TextInput(
        hint_text='Service Category',
        text=service_data.get('category', '')
    )
    description_input = TextInput(
        hint_text='Service Description',
        text=service_data.get('description', '')
    )
    value_input = TextInput(
        hint_text='JOULE Value',
        input_filter='int',
        text=str(service_data.get('value', '') or '')
    )

    err_label = Label(text='', size_hint_y=None, height=25, color=(1, 0.3, 0.3, 1))

    save_button = Button(text='Save')
    cancel_button = Button(text='Cancel')

    def save_service(_):
        category = category_input.text.strip()
        description = description_input.text.strip()
        raw_value = value_input.text.strip() or '0'

        if not category:
            err_label.text = 'Category is required.'
            return
        try:
            value = int(raw_value)
        except ValueError:
            err_label.text = 'Value must be a whole number.'
            return

        if is_edit:
            # Preserve identity fields, refresh only user-editable ones.
            updated = dict(service_data)
            updated['category'] = category
            updated['description'] = description
            updated['value'] = str(value)
            updated['last_edited'] = datetime.utcnow().isoformat()
        else:
            updated = {
                'timestamp': datetime.utcnow().isoformat(),
                'category': category,
                'description': description,
                'value': str(value),
                'provider_id': screen.user_id,
            }

        if on_saved is not None:
            on_saved(updated)
        else:
            # Default persistence: append or replace within the provider's list.
            services = screen.data_handler.load_services(screen.user_id)
            if is_edit:
                for i, s in enumerate(services):
                    if s is service_data or s == service_data:
                        services[i] = updated
                        break
                else:
                    services.append(updated)
            else:
                services.append(updated)
            screen.data_handler.overwrite_services(services, screen.user_id)
            screen.load_services(global_view=True)

        popup.dismiss()

    save_button.bind(on_press=save_service)
    cancel_button.bind(on_press=lambda _: popup.dismiss())

    layout.add_widget(category_input)
    layout.add_widget(description_input)
    layout.add_widget(value_input)
    layout.add_widget(err_label)
    layout.add_widget(save_button)
    layout.add_widget(cancel_button)

    title = 'Edit Service' if is_edit else 'Add a Service'
    popup = Popup(title=title, content=layout, size_hint=(0.85, 0.7))
    popup.open()
    return popup