# service_task_receipt.py

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from utils.data_handler import DataHandler

class ServiceTaskReceipt(Screen):
    def __init__(self, user_id, category, description, value):
        super().__init__()
        self.user_id = user_id
        self.category = category
        self.description = description
        self.value = int(value)
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def generate_hash(self):
        # Hash the service data for integrity and JOULES transfer proof
        data_string = f"{self.user_id}{self.category}{self.description}{self.value}{self.timestamp}"
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def save_receipt_data(self, directory='receipts'):
        if not os.path.exists(directory):
            os.makedirs(directory)

        receipt_data = {
            'user_id': self.user_id,
            'category': self.category,
            'description': self.description,
            'value': self.value,
            'timestamp': self.timestamp,
            'hash': self.generate_hash()
        }

        safe_user_id = str(self.user_id).replace(' ', '_')
        safe_timestamp = self.timestamp.replace(' ', '_').replace(':', '-')
        filename = f"{directory}/receipt_{safe_user_id}_{safe_timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(receipt_data, f, indent=4)

        return filename  # ✅ Return it so it can optionally be reused

    def create_receipt_image(self, filename=None, directory='receipts'):
        if not filename:
            import re
            safe_user_id = re.sub(r'\W+', '_', str(self.user_id))
            safe_timestamp = self.timestamp.replace(' ', '_').replace(':', '-')
            filename = f"{directory}/receipt_{safe_user_id}_{safe_timestamp}.png"

        # Create a simple receipt image with PIL
        width, height = 400, 250
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            font = ImageFont.load_default()

        lines = [
            f"Service Receipt",
            f"User ID: {self.user_id}",
            f"Category: {self.category}",
            f"Description: {self.description}",
            f"Value: {self.value}",
            f"Timestamp: {self.timestamp}",
            f"Hash: {self.generate_hash()[:256]}..." # Current full hash for auditing purposes.
        ]

        y = 20
        for line in lines:
            draw.text((20, y), line, fill='black', font=font)
            y += 25

        image.save(filename)
        return filename

class PaymentWindow(Popup):
    def __init__(self, user_id, recipient_id, service_data, on_transaction_complete=None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.recipient_id = recipient_id
        self.service_data = service_data
        self.data_handler = DataHandler()
        self.on_transaction_complete = on_transaction_complete

        print("Opening PaymentWindow with:", user_id, service_data)

        self.title = "Confirm JOULES Transfer"
        self.size_hint = (0.85, 0.6)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(
        Label(text=f"Service: {service_data.get('description') or service_data.get('task_name', 'Unknown')}", font_size=16))
        layout.add_widget(Label(text=f"Value: {service_data['value']} JOULES"))
        layout.add_widget(Label(text=f"From: {self.user_id}"))
        layout.add_widget(Label(text=f"To: {self.recipient_id}"))

        self.note_input = TextInput(hint_text="Optional note", multiline=False)
        layout.add_widget(self.note_input)

        self.error_label = Label(text='', color=(1, 0, 0, 1), size_hint_y=None, height=30)
        layout.add_widget(self.error_label)

        confirm_button = Button(text="Confirm Transfer")
        cancel_button = Button(text="Cancel")

        confirm_button.bind(on_press=self.transfer_joules)
        cancel_button.bind(on_press=lambda _: self.dismiss())

        layout.add_widget(confirm_button)
        layout.add_widget(cancel_button)

        self.content = layout

    def transfer_joules(self, _):
        value = int(self.service_data['value'])

        if self.user_id == self.recipient_id:
            self.error_label.text = "Cannot transfer JOULES to your own account."
            return

        payer_balance = self.data_handler.get_user_balance(self.user_id, default=250000)
        recipient_balance = self.data_handler.get_user_balance(self.recipient_id, default=0)

        if payer_balance >= value:
            self.data_handler.set_user_balance(self.user_id, payer_balance - value)
            self.data_handler.set_user_balance(self.recipient_id, recipient_balance + value)

            # Safe fallback for missing keys
            description = self.service_data.get('description') or self.service_data.get('task_name', 'No description')

            receipt = ServiceTaskReceipt(
                self.user_id,
                self.service_data['category'],
                description,
                value
            )
            receipt.save_receipt_data()
            receipt.create_receipt_image()

            if self.on_transaction_complete:
                self.on_transaction_complete()

            self.dismiss()
        else:
            self.error_label.text = "Insufficient JOULES balance."



