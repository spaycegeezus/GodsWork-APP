# ledger_viewer.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty
from gw_screen import get_db_path
from gw_screen.account import AccountScreen
from utils.data_handler import DataHandler  # Import your DataHandler
import json
import os
import csv
import datetime

LEDGER_PATH = "data_ledger.json"
TASKS_PATH = "data/anonymous.json"
PROFILES_DIR = "data/profiles"


class LedgerViewerScreen(Screen):
    transactions = ListProperty([])
    current_user = StringProperty("")  # Track current user for color coding

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_handler = DataHandler()  # Initialize your data handler
        self.anonymize = False
        self.search_term = ""
        self.show_tasks = True

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Toolbar
        tool_bar = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        self.search_input = TextInput(hint_text='Search transactions...', multiline=False)
        search_btn = Button(text='Search')
        search_btn.bind(on_press=self.search_transactions)

        # Toggle for showing tasks
        self.tasks_toggle = Button(text='Hide Tasks')
        self.tasks_toggle.bind(on_press=self.toggle_tasks)

        export_btn = Button(text='Export CSV')
        export_btn.bind(on_press=self.export_to_csv)

        tool_bar.add_widget(self.search_input)
        tool_bar.add_widget(search_btn)
        tool_bar.add_widget(self.tasks_toggle)
        tool_bar.add_widget(export_btn)
        self.layout.add_widget(tool_bar)

        # Home button
        home_btn = Button(text='Back to Home', size_hint=(0.6, None), height=40, pos_hint={'center_x': 0.5})
        home_btn.bind(on_press=self.go_home)
        self.layout.add_widget(home_btn)

        # Title
        self.layout.add_widget(Label(text='Transparent Ledger Viewer', font_size=24, size_hint=(1, None), height=40))

        # Refresh
        self.refresh_button = Button(text='Refresh', size_hint=(1, None), height=40)
        self.refresh_button.bind(on_press=self.load_combined_data)
        self.layout.add_widget(self.refresh_button)

        # Scrollable ledger
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        self.layout.add_widget(self.scroll)

        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        """Load data when screen is about to be shown"""
        self.load_combined_data()

    def set_current_user(self, username):
        """Set the current user for transaction coloring"""
        self.current_user = username
        self.load_combined_data()

    def toggle_tasks(self, instance):
        """Toggle task visibility"""
        self.show_tasks = not self.show_tasks
        self.tasks_toggle.text = 'Show Tasks' if not self.show_tasks else 'Hide Tasks'
        self.load_combined_data()

    def set_anonymize(self, anon_state):
        self.anonymize = anon_state
        self.load_combined_data()

    def update_ledger(self, new_transactions):
        self.transactions = new_transactions
        self.display_combined_data(new_transactions)

    def color_for_entry(self, entry, entry_type="transaction"):
        """Decide color based on entry type and content"""
        if entry_type == "task":
            # Color coding for tasks - ensure joules is a number
            joules = entry.get("joules", entry.get("value", 0))
            # Convert to float/int if it's a string
            try:
                joules = float(joules) if isinstance(joules, str) else joules
            except (ValueError, TypeError):
                joules = 0

            if joules > 1000:
                return "[color=FFD700]"  # Gold for high-energy tasks
            elif joules > 100:
                return "[color=32CD32]"  # Green for medium-energy tasks
            else:
                return "[color=87CEEB]"  # Light blue for low-energy tasks
        else:
            # Transaction coloring - ensure amount is a number
            amount = entry.get("amount", 0)
            # Convert to float/int if it's a string
            try:
                amount = float(amount) if isinstance(amount, str) else amount
            except (ValueError, TypeError):
                amount = 0

            flagged = entry.get("flagged", False)

            if flagged or amount > 10000:
                return "[color=FFD700]"  # Yellow for flagged/large transactions
            elif entry.get("to") == self.current_user:
                return "[color=32CD32]"  # Green (incoming to current user)
            else:
                return "[color=FF4500]"  # Red (outgoing from current user)

    def format_task_entry(self, task):
        """Format a task for display - matches account.py task structure"""
        user_id = task.get('user_id', 'anonymous')
        description = task.get('description', task.get('task_name', 'No description'))
        joules = task.get('joules', task.get('value', 0))
        category = task.get('category', 'uncategorized')
        timestamp = task.get('timestamp', '')
        weight = task.get('weight', 0)

        if self.anonymize:
            user_id = str(hash(user_id)) % 1000000

        color_tag = self.color_for_entry(task, "task")

        return (
            f"{color_tag}[TASK] {user_id} | {category} | {joules} J[/color]\n"
            f"Description: {description} | Weight: {weight} kg\n"
            f"Time: {timestamp}"
        )

    def format_transaction_entry(self, transaction):
        """Format a transaction for display - matches account.py transaction structure"""
        from_user = str(hash(transaction['from'])) % 1000000 if self.anonymize else transaction['from']
        to_user = str(hash(transaction['to'])) % 1000000 if self.anonymize else transaction['to']
        amount = transaction.get("amount", 0)
        timestamp = transaction.get("timestamp", "")
        tx_hash = transaction.get("hash", "")[:12]

        color_tag = self.color_for_entry(transaction, "transaction")

        return (
            f"{color_tag}[TX] {from_user} → {to_user} | {amount} J[/color]\n"
            f"Hash: {tx_hash}... | Time: {timestamp}"
        )

    def display_combined_data(self, entries):
        """Display both transactions and tasks"""
        self.grid.clear_widgets()

        if not entries:
            self.grid.add_widget(Label(text='No entries yet.', font_size=16))
            return

        for entry in entries:
            entry_type = entry.get("type", "transaction")

            if entry_type == "task" and not self.show_tasks:
                continue  # Skip tasks if they're hidden

            if entry_type == "task":
                formatted_text = self.format_task_entry(entry)
                box_height = 100  # More height for tasks with details
            else:
                formatted_text = self.format_transaction_entry(entry)
                box_height = 80

            box = BoxLayout(orientation='vertical', size_hint_y=None, padding=10)
            box.height = box_height

            label = Label(
                text=formatted_text,
                size_hint_y=None,
                height=box_height - 20,
                halign='left',
                valign='middle',
                markup=True,
                text_size=(None, None)
            )
            label.bind(width=lambda inst, val: setattr(inst, 'text_size', (val - 20, None)))

            box.add_widget(label)
            self.grid.add_widget(box)

    def search_transactions(self, instance):
        query = self.search_input.text.strip().lower()
        filtered = [
            entry for entry in self.transactions
            if query in json.dumps(entry).lower()
        ]
        self.display_combined_data(filtered)

    def export_to_csv(self, instance):
        filename = f'ledger_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ['Type', 'From/User', 'To/Category', 'Amount/Joules', 'Description', 'Weight', 'Timestamp', 'Hash'])
            for entry in self.transactions:
                entry_type = entry.get("type", "transaction")
                if entry_type == "task":
                    writer.writerow([
                        'TASK',
                        entry.get('user_id', ''),
                        entry.get('category', ''),
                        entry.get('joules', entry.get('value', 0)),
                        entry.get('description', entry.get('task_name', '')),
                        entry.get('weight', 0),
                        entry.get('timestamp', ''),
                        ''
                    ])
                else:
                    writer.writerow([
                        'TRANSACTION',
                        entry.get('from', ''),
                        entry.get('to', ''),
                        entry.get('amount', 0),
                        '',
                        '',
                        entry.get('timestamp', ''),
                        entry.get('hash', '')[:12]
                    ])
        print(f"Ledger exported to {filename}")

    def load_tasks(self):
        """Load tasks using DataHandler to match account.py"""
        all_tasks = []

        # Load tasks from DataHandler (matches account.py approach)
        try:
            # Load anonymous tasks
            anonymous_tasks = self.data_handler.load_tasks(user_id=None)
            for task in anonymous_tasks:
                task['type'] = 'task'
                task['user_id'] = 'anonymous'
            all_tasks.extend(anonymous_tasks)

            # Load user tasks
            user_tasks = self.data_handler.load_all_entries(user_id=None)
            for task in user_tasks:
                if task.get('type') == 'task' or 'task_name' in task:
                    task['type'] = 'task'
                    if 'user_id' not in task:
                        task['user_id'] = 'unknown'
            all_tasks.extend([t for t in user_tasks if t.get('type') == 'task'])

        except Exception as e:
            print(f"Error loading tasks: {e}")

        return all_tasks

    def load_transactions(self):
        """Load transactions from ledger file - matches account.py format"""
        if not os.path.exists(LEDGER_PATH):
            return []

        try:
            with open(LEDGER_PATH, "r") as f:
                ledger = json.load(f)

            # Add type identifier and ensure proper format
            for transaction in ledger:
                transaction['type'] = 'transaction'
                # Ensure all required fields exist
                transaction.setdefault('from', 'unknown')
                transaction.setdefault('to', 'unknown')
                transaction.setdefault('amount', 0)
                transaction.setdefault('timestamp', '')
                transaction.setdefault('hash', '')

            return ledger
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def load_combined_data(self, *args):
        """Load both transactions and tasks, then combine and sort them"""
        transactions = self.load_transactions()
        tasks = self.load_tasks() if self.show_tasks else []

        # Combine and sort by timestamp (newest first)
        all_entries = transactions + tasks
        all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Filter by search term if any
        if self.search_term:
            all_entries = [
                entry for entry in all_entries
                if self.search_term in json.dumps(entry).lower()
            ]

        self.transactions = all_entries
        self.display_combined_data(all_entries)

    def go_home(self, instance):
        self.manager.current = 'home'