from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# this is ui_components.py
class ServiceItem(BoxLayout):
    def __init__(self, service_data, on_delete, on_edit, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=40, spacing=10, **kwargs)

        self.service_data = service_data
        self.on_delete = on_delete
        self.on_edit = on_edit

        self.label = Label(
            text=self._format_text(),
            halign='left',
            valign='middle'
        )
        self.label.bind(size=self.label.setter('text_size'))

        self.edit_btn = Button(text='Pay', size_hint=(None, 1), width=70, on_press=self.edit_service)
        self.del_btn = Button(text='Delete', size_hint=(None, 1), width=70, on_press=self.delete_service)

        self.add_widget(self.label)
        self.add_widget(self.edit_btn)
        self.add_widget(self.del_btn)

    def _format_text(self):
        return f"{self.service_data.get('timestamp', 'N/A')} | " \
               f"{self.service_data.get('category', 'Uncategorized')} - " \
               f"{self.service_data.get('description', 'No description')} " \
               f"({self.service_data.get('value', 0)} JOULES)"

    def delete_service(self, instance):
        self.on_delete(self)

    def edit_service(self, instance):
        self.on_edit(self)
