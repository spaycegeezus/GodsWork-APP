#this is account.py

from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.graphics import Rectangle, Color
from utils.data_handler import PREDEFINED_TASKS, DataHandler
from gw_screen.custom_task_popup import CustomTaskPopup
from datetime import datetime
from eth_hash.auto import keccak
import json
import os

LEDGER_PATH = "data_ledger.json"


def keccak256_hash(data: str) -> str:
    return keccak(data.encode()).hex()


class AccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_handler = DataHandler()
        self.selected_category = None
        self.selected_task = None
        self.current_username = ""

        # Initialize ALL widgets first
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Username section - ADD TEXT BINDING HERE
        username_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        self.username_input = TextInput(
            hint_text='Enter Username',
            size_hint=(0.7, 1),
            multiline=False
        )
        # ADD THIS BINDING - this is what you're missing
        self.username_input.bind(text=self.on_username_text_change)

        self.username_submit = Button(
            text='Load Account',
            size_hint=(0.3, 1)
        )
        self.username_submit.bind(on_press=self.submit_username)
        username_layout.add_widget(self.username_input)
        username_layout.add_widget(self.username_submit)
        self.layout.add_widget(username_layout)

        # Balance label
        self.balance_label = Label(text='Balance: 250000 JOULES', font_size=24, size_hint=(1, None), height=40)
        self.layout.add_widget(self.balance_label)

        # Transfer section
        self.transfer_input = TextInput(hint_text='Amount to transfer', size_hint=(1, None), height=40,
                                        input_filter='int')
        self.device_input = TextInput(hint_text='Destination account/device', size_hint=(1, None), height=40)
        self.transfer_result = Label(text='', size_hint=(1, None), height=30)
        self.transfer_button = Button(text='Transfer', size_hint=(1, None), height=40)
        self.transfer_button.bind(on_press=self.transfer_funds)

        self.layout.add_widget(self.transfer_input)
        self.layout.add_widget(self.device_input)
        self.layout.add_widget(self.transfer_button)
        self.layout.add_widget(self.transfer_result)

        # Task selection
        self.category_spinner = Spinner(text='Select Category', values=list(PREDEFINED_TASKS.keys()),
                                        size_hint=(1, None), height=44)
        self.task_spinner = Spinner(text='Select Task', size_hint=(1, None), height=44)
        self.category_spinner.bind(text=self.update_tasks)
        self.task_spinner.bind(text=self.set_selected_task)
        self.layout.add_widget(self.category_spinner)
        self.layout.add_widget(self.task_spinner)

        # Weight slider
        self.weight_label = Label(text='Multiplier: Weight(kg), Time(Hr/min): 1.0', size_hint=(1, None), height=30)
        self.weight_slider = Slider(min=0.5, max=50.0, value=1.0, step=0.5, size_hint=(1, None), height=40)
        self.weight_slider.bind(value=self.update_weight_label)
        self.layout.add_widget(self.weight_label)
        self.layout.add_widget(self.weight_slider)

        # Action buttons
        self.report_button = Button(text='Report Completed Task', size_hint=(1, None), height=40)
        self.report_button.bind(on_press=self.report_task)
        self.layout.add_widget(self.report_button)

        custom_btn = Button(text='Add Custom Task', size_hint=(1, None), height=40)
        custom_btn.bind(on_press=self.open_custom_task_popup)
        self.layout.add_widget(custom_btn)

        home_btn = Button(text='Back to Home', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5})
        home_btn.bind(on_press=self.go_home)
        self.layout.add_widget(home_btn)

        # Add layout to screen LAST
        self.add_widget(self.layout)

        # Reset if new year
        self.reset_if_new_year()

    def on_username_text_change(self, instance, value):
        """This is the missing piece - bind this to text changes"""
        username = value.strip()
        print(f"Username text changed to: '{username}'")
        self.current_username = username
        if username:
            self.load_balance_from_username()

    def on_pre_enter(self, *args):
        print("AccountScreen on_pre_enter called")
        self.transfer_result.text = ''
        self.transfer_input.text = ''
        self.device_input.text = ''

        # Only reset if no username known
        if not self.current_username:
            self.username_input.text = ""
            self.balance_label.text = 'Balance: 250000 JOULES'
        else:
            self.username_input.text = self.current_username
            self.load_balance_from_username()

    def submit_username(self, instance):
        """Explicitly set username when button is pressed"""
        username = self.username_input.text.strip()
        print(f"Submit username pressed: '{username}'")

        if not username:
            self.transfer_result.text = "Please enter a username"
            return

        self.current_username = username
        self.load_balance_from_username()
        self.transfer_result.text = f"Account loaded: {username}"

    def load_balance_from_username(self):
        """Load balance for current username"""
        if not self.current_username:
            print("No username to load balance for")
            return

        print(f"Loading balance for: '{self.current_username}'")
        try:
            balance = self.data_handler.get_user_balance(self.current_username)
            print(f"Raw balance retrieved: {balance}")
            self.balance_label.text = f"Balance: {int(balance)} JOULES"
            print(f"Balance displayed: {int(balance)} JOULES")
        except Exception as e:
            print(f"Error loading balance: {e}")
            self.balance_label.text = "Balance: Error"

    def check_username_loaded(self):
        """Check if username is loaded and show error if not"""
        if not self.current_username:
            self.transfer_result.text = "Please enter a username first"
            return False
        return True

    def add_to_balance(self, amount):
        if not self.check_username_loaded():
            return

        try:
            balance = self.data_handler.get_user_balance(self.current_username)
            new_balance = balance + amount
            self.data_handler.set_user_balance(self.current_username, new_balance)
            self.update_balance()
        except Exception as e:
            print(f"Error adding to balance: {e}")

    def transfer_funds(self, instance):
        print("Transfer funds button pressed")
        if not self.check_username_loaded():
            return

        amount_text = self.transfer_input.text.strip()
        device = self.device_input.text.strip()

        if not amount_text.isdigit():
            self.transfer_result.text = "Enter a valid amount"
            return

        if not device:
            self.transfer_result.text = "Enter a valid destination"
            return

        if not self.data_handler.user_exists(device):
            self.transfer_result.text = f"Destination '{device}' does not exist. Please create an account first."
            return

        amount = int(amount_text)
        current_balance = self.data_handler.get_user_balance(self.current_username)

        if amount > current_balance:
            self.transfer_result.text = "Insufficient funds"
            return

        # Perform transfer
        self.data_handler.set_user_balance(self.current_username, current_balance - amount)
        receiver_balance = self.data_handler.get_user_balance(device)
        self.data_handler.set_user_balance(device, receiver_balance + amount)

        # Make sure display is updated
        self.update_balance()
        self.transfer_result.text = f"Transferred {amount} JOULES to {device}"

    def update_weight_label(self, instance, value):
        self.weight_label.text = f'Weight/Time: {value:.1f} kg/(Hr,Min)'

    def log_transaction(self, to, amount):
        now = datetime.utcnow().isoformat()
        tx_data = f"{self.current_username}->{to}:{amount}@{now}"
        tx_hash = keccak256_hash(tx_data)
        entry = {"from": self.current_username, "to": to, "amount": amount, "timestamp": now, "hash": tx_hash}

        if not os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH, "w") as f:
                json.dump([], f, indent=2)

        with open(LEDGER_PATH, "r+") as f:
            ledger = json.load(f)
            ledger.append(entry)
            f.seek(0)
            json.dump(ledger, f, indent=2)

    def report_task(self, instance):
        print("Report task button pressed")
        if not self.check_username_loaded():
            return

        if not self.selected_task:
            self.transfer_result.text = 'Please select a task.'
            return

        weight = self.weight_slider.value
        base_joules = self.selected_task.get('joules', 0)
        base_weight = self.selected_task.get('weight', 1)
        scaled_joules = (base_joules / base_weight) * weight

        task_data = {
            "task_name": self.selected_task['name'],
            "category": self.selected_task['category'],
            "value": scaled_joules,
            "weight": weight,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Self-reported"
        }

        self.data_handler.save_task(task_data, self.current_username)
        self.add_to_balance(scaled_joules)
        self.transfer_result.text = f"Added {int(scaled_joules)} JOULES for {weight:.1f} kg of {self.selected_task['name']}"
        self.selected_task = None
        self.task_spinner.text = 'Select Task'
        self.weight_slider.value = 1.0

    def update_balance(self):
        """Reload and display the current balance from persistent storage."""
        if not self.current_username:
            self.balance_label.text = "Balance: 250000 JOULES"
            return

        balance = self.data_handler.get_user_balance(self.current_username)
        self.balance_label.text = f"Balance: {int(balance)} JOULES"

    def update_tasks(self, spinner, category):
        self.selected_category = category
        self.task_spinner.values = [task['name'] for task in PREDEFINED_TASKS[category]]

    def set_selected_task(self, spinner, task_name):
        for task in PREDEFINED_TASKS.get(self.selected_category, []):
            if task['name'] == task_name:
                self.selected_task = task
                self.selected_task['category'] = self.selected_category
                break

    def open_custom_task_popup(self, instance):
        print("Opening custom task popup...")
        if not self.check_username_loaded():
            return
        print(f"Username '{self.current_username}' found - opening popup")
        CustomTaskPopup(on_submit=self.handle_submit).open()

    def handle_submit(self, category, description, value, weight, time):
        print(f"Custom task submitted: {category}, {description}, {value}, {weight}, {time}")

        if not self.current_username:
            self.transfer_result.text = "Please enter your username first"
            print("ERROR: Username lost during popup submission!")
            return

        try:
            # Log the task for this user
            print(f"Logging task for user: {self.current_username}")
            self.data_handler.log_self_reported_task(
                category,
                description,
                value,
                self.current_username,
                weight,
                time
            )

            # Update the balance for this same user
            print(f"Adding {value} joules to balance")
            self.data_handler.add_to_balance(self.current_username, value)

            # Refresh the displayed balance on screen
            self.update_balance()

            # Give user confirmation feedback
            self.transfer_result.text = f"✅ Task '{description}' logged and +{value} Joules added!"
            print("Custom task completed successfully")

        except Exception as e:
            print(f"Error in handle_submit: {e}")
            self.transfer_result.text = f"Error saving task: {str(e)}"

    def reset_if_new_year(self):
        year = datetime.now().year
        ledger_flag = f"data/reset_{year}.flag"
        os.makedirs(os.path.dirname(ledger_flag), exist_ok=True)
        if not os.path.exists(ledger_flag):
            with open(ledger_flag, "w") as f:
                f.write("reset done")

    def go_home(self, instance):
        self.manager.current = 'home'

    def go_service(self, instance):
        self.manager.current = 'service'