#this is account.py

from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from utils.lux_ui import RoundedButton, RoundedTextInput, RoundedSpinner, LuxCard, vertical_gradient, GOLD, EMERALD, SAPPHIRE, AMETHYST, ROSE, TEXT, TEXT_DIM, INK_TOP, INK_BOTTOM
from kivy.uix.slider import Slider
from kivy.graphics import Rectangle, Color
from utils.data_handler import PREDEFINED_TASKS, DataHandler, LEDGER_PATH
from utils.service_popups import open_service_popup
from gw_screen.custom_task_popup import CustomTaskPopup, TaskFormPopup
from datetime import datetime
from eth_hash.auto import keccak
import json
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
import os

def keccak256_hash(data: str) -> str:
    return keccak(data.encode()).hex()

def show_json_editor(title, initial_data, on_save):
    """Small JSON sub-popup. Used for editing arbitrary service/task schemas."""
    content = BoxLayout(orientation='vertical', spacing=6, padding=6)
    editor = TextInput(text=json.dumps(initial_data, indent=2), multiline=True)
    content.add_widget(editor)

    err = Label(text='', size_hint_y=None, height=25, color=(1, 0.3, 0.3, 1))
    content.add_widget(err)

    btn_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
    save_btn = Button(text='Save')
    cancel_btn = Button(text='Cancel')
    btn_row.add_widget(save_btn)
    btn_row.add_widget(cancel_btn)
    content.add_widget(btn_row)

    popup = Popup(title=title, content=content, size_hint=(0.9, 0.8))

    def do_save(instance):
        try:
            data = json.loads(editor.text)
        except json.JSONDecodeError as e:
            err.text = f"Invalid JSON: {e}"
            return
        on_save(data)
        popup.dismiss()

    save_btn.bind(on_press=do_save)
    cancel_btn.bind(on_press=popup.dismiss)
    popup.open()

class AccountScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_handler = DataHandler()
        self.selected_category = None
        self.selected_task = None
        self.current_username = ""

        # ---------- gradient backdrop ----------
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._bg_rect = Rectangle(
                texture=vertical_gradient(INK_TOP, INK_BOTTOM)
            )
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        # ---------- scroll root ----------
        root = BoxLayout(orientation='vertical')
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self.layout = BoxLayout(
            orientation='vertical',
            padding=dp(18), spacing=dp(14),
            size_hint_y=None,
        )
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll.add_widget(self.layout)
        root.add_widget(scroll)
        self.add_widget(root)

        # =========================================================
        # CARD 1 — IDENTITY
        # =========================================================
        id_card = LuxCard()

        id_card.add_widget(Label(
            text='[b]A C C O U N T[/b]', markup=True,
            color=TEXT, font_size=dp(13),
            size_hint_y=None, height=dp(20),
        ))

        username_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None, height=dp(48), spacing=dp(10),
        )
        self.username_input = RoundedTextInput(
            hint_text='Enter Username',
            size_hint=(0.68, 1),
            multiline=False,
        )
        self.username_input.bind(text=self.on_username_text_change)

        self.username_submit = RoundedButton(
            text='Load Account',
            bg_color=GOLD,
            size_hint=(0.32, 1),
        )
        self.username_submit.bind(on_press=self.submit_username)
        username_layout.add_widget(self.username_input)
        username_layout.add_widget(self.username_submit)
        id_card.add_widget(username_layout)

        self.balance_label = Label(
            text='Balance: 250000 JOULES',
            font_size=dp(26), bold=True,
            color=GOLD,
            size_hint_y=None, height=dp(46),
        )
        id_card.add_widget(self.balance_label)
        self.layout.add_widget(id_card)

        # =========================================================
        # CARD 2 — TRANSFER
        # =========================================================
        tx_card = LuxCard()

        tx_card.add_widget(Label(
            text='[b]T R A N S F E R[/b]', markup=True,
            color=TEXT, font_size=dp(12),
            size_hint_y=None, height=dp(18),
        ))

        self.transfer_input = RoundedTextInput(
            hint_text='Amount to transfer',
            size_hint=(1, None), height=dp(46),
            input_filter='int',
        )
        self.device_input = RoundedTextInput(
            hint_text='Destination account / device',
            size_hint=(1, None), height=dp(46),
        )
        self.transfer_button = RoundedButton(
            text='Send JOULES',
            bg_color=SAPPHIRE,
            size_hint=(1, None), height=dp(48),
        )
        self.transfer_button.bind(on_press=self.transfer_funds)

        self.transfer_result = Label(
            text='',
            color=EMERALD,
            size_hint_y=None, height=dp(26),
        )

        tx_card.add_widget(self.transfer_input)
        tx_card.add_widget(self.device_input)
        tx_card.add_widget(self.transfer_button)
        tx_card.add_widget(self.transfer_result)
        self.layout.add_widget(tx_card)

        # =========================================================
        # CARD 3 — TASKS
        # =========================================================
        task_card = LuxCard()

        task_card.add_widget(Label(
            text='[b]T A S K S[/b]', markup=True,
            color=TEXT, font_size=dp(12),
            size_hint_y=None, height=dp(18),
        ))

        self.category_spinner = RoundedSpinner(
            text='Select Category',
            values=list(PREDEFINED_TASKS.keys()),
            size_hint=(1, None), height=dp(46),
        )
        self.task_spinner = RoundedSpinner(
            text='Select Task',
            size_hint=(1, None), height=dp(46),
        )
        self.category_spinner.bind(text=self.update_tasks)
        self.task_spinner.bind(text=self.set_selected_task)

        task_card.add_widget(self.category_spinner)
        task_card.add_widget(self.task_spinner)

        self.weight_label = Label(
            text='Multiplier: Weight(kg), Time(Hr/min): 1.0',
            color=TEXT_DIM,
            size_hint_y=None, height=dp(26),
        )
        self.weight_slider = Slider(
            min=0.5, max=50.0, value=1.0, step=0.5,
            size_hint=(1, None), height=dp(40),
            cursor_size=(dp(26), dp(26)),
        )
        self.weight_slider.bind(value=self.update_weight_label)

        task_card.add_widget(self.weight_label)
        task_card.add_widget(self.weight_slider)

        self.report_button = RoundedButton(
            text='Report Completed Task',
            bg_color=EMERALD,
            size_hint=(1, None), height=dp(48),
        )
        self.report_button.bind(on_press=self.report_task)
        task_card.add_widget(self.report_button)

        custom_btn = RoundedButton(
            text='+ Add Custom Task',
            bg_color=AMETHYST,
            size_hint=(1, None), height=dp(46),
        )
        custom_btn.bind(on_press=self.open_custom_task_popup)
        task_card.add_widget(custom_btn)

        self.layout.add_widget(task_card)

        # =========================================================
        # BACK BUTTON
        # =========================================================
        home_btn = RoundedButton(
            text='Back to Home',
            bg_color=ROSE,
            size_hint=(0.6, None), height=dp(44),
            pos_hint={'center_x': 0.5},
        )
        home_btn.bind(on_press=self.go_home)
        self.layout.add_widget(home_btn)

        self.reset_if_new_year()

    # ---- backdrop helper (add once) ----
    def _sync_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

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
        username = self.username_input.text.strip()
        print(f"Submit username pressed: '{username}'")

        if not username:
            self.transfer_result.text = "Please enter a username"
            return

        self.current_username = username
        self.load_balance_from_username()
        self.transfer_result.text = f"Account loaded: {username}"

    def load_balance_from_username(self):
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

    def is_admin(self):
        profile = self.data_handler.load_user_profile(self.current_username)
        return profile.get("admin", False)

    def check_username_loaded(self):
        input_username = self.username_input.text.strip()
        if input_username:
            self.current_username = input_username
        elif not self.current_username:
            self.transfer_result.text = "Please enter a username first"
            return False
        return True

    def report_task(self, instance):
        if not self.check_username_loaded():
            return

        if not self.selected_task:
            self.transfer_result.text = 'Please select a task.'
            return

        weight = self.weight_slider.value
        base_joules = self.selected_task.get('joules', 0)
        base_weight = self.selected_task.get('weight', 1)
        scaled_joules = int((base_joules / base_weight) * weight)

        # Admin/system-originated credit
        transaction = self.data_handler.update_balance_with_transaction(
            from_user=None,  # system source
            to_user=self.current_username,
            amount=scaled_joules,
            transaction_type="task_completion",
            metadata={
                "task_name": self.selected_task['name'],
                "category": self.selected_task['category'],
                "weight": weight
            },
            admin=self.is_admin()  # 🟣 FLAG
        )

        # Save task linked to ledger
        self.data_handler.save_task({
            "task_name": self.selected_task['name'],
            "category": self.selected_task['category'],
            "value": scaled_joules,
            "weight": weight,
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_hash": transaction["hash"]
        }, self.current_username)

        self.update_balance()
        self.transfer_result.text = f"Added {scaled_joules} JOULES"

        self.selected_task = None
        self.task_spinner.text = 'Select Task'
        self.weight_slider.value = 1.0

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
        input_username = self.username_input.text.strip()
        if input_username:
            self.current_username = input_username

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

        # This method updates balances AND writes to ledger in one go
        try:
            transaction = self.data_handler.update_balance_with_transaction(
                from_user=self.current_username,
                to_user=device,
                amount=amount,
                transaction_type="peer_transfer"
            )
            self.update_balance()
            self.transfer_result.text = f"Transferred {amount} JOULES to {device}"
        except Exception as e:
            self.transfer_result.text = f"Transfer failed: {e}"
            print(f"Transfer error: {e}")

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

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_handler = DataHandler()
        layout = BoxLayout(orientation='vertical')
        self.current_username = ""
        self.user_id = "admin"

        # Toolbar
        toolbar = BoxLayout(size_hint_y=None, height=50)
        back_btn = Button(text='Back')
        back_btn.bind(on_press=self.go_back)
        refresh_btn = Button(text='Refresh')
        refresh_btn.bind(on_press=self.refresh_users)
        toolbar.add_widget(back_btn)
        toolbar.add_widget(refresh_btn)
        layout.add_widget(toolbar)

        # Scrollable user list
        self.scroll = ScrollView()
        self.user_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.user_grid.bind(minimum_height=self.user_grid.setter('height'))
        self.scroll.add_widget(self.user_grid)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def on_pre_enter(self):
        self.refresh_users()

    def refresh_users(self, *args):
        self.user_grid.clear_widgets()
        users = self.data_handler.get_all_users()
        for username in users:
            self.user_grid.add_widget(self.build_user_row(username))

    def build_user_row(self, username):
        row = BoxLayout(size_hint_y=None, height=60, spacing=5)
        row.add_widget(Label(text=username, size_hint_x=0.3))

        balance = self.data_handler.get_user_balance(username)
        row.add_widget(Label(text=f"{balance} J", size_hint_x=0.2))

        # Buttons
        delete_btn = Button(text='Delete', size_hint_x=0.2)
        delete_btn.bind(on_press=lambda x, u=username: self.delete_user(u))
        adjust_btn = Button(text='Adjust', size_hint_x=0.2)
        adjust_btn.bind(on_press=lambda x, u=username: self.show_adjust_popup(u))
        edit_btn = Button(text='Edit', size_hint_x=0.2)
        edit_btn.bind(on_press=lambda x, u=username: self.show_edit_popup(u))

        row.add_widget(delete_btn)
        row.add_widget(adjust_btn)
        row.add_widget(edit_btn)
        return row

    def delete_user(self, username):
        # Confirmation popup
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=f"Are you sure you want to delete {username}?"))
        btn_layout = BoxLayout(size_hint_y=0.3)
        confirm_btn = Button(text='Yes')
        cancel_btn = Button(text='No')
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.4))
        confirm_btn.bind(on_press=lambda x: self._do_delete(username, popup))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def _do_delete(self, username, popup):
        self.data_handler.delete_user(username)
        popup.dismiss()
        self.refresh_users()

    def show_adjust_popup(self, username):
        """Popup to add to, subtract from, or set a user's balance."""

        content = BoxLayout(orientation='vertical', spacing=8, padding=10)

        # --- Header + live balance ---
        content.add_widget(Label(
            text=f"[b]{username}[/b]", markup=True,
            size_hint_y=None, height=25
        ))
        balance_label = Label(
            text=f"Balance: {self.data_handler.get_user_balance(username)} J",
            size_hint_y=None, height=30
        )
        content.add_widget(balance_label)

        # --- Mode selector ---
        mode_row = BoxLayout(size_hint_y=None, height=40, spacing=5)
        add_tb = ToggleButton(text='Add', group='adjust_mode',
                              state='down', allow_no_selection=False)
        sub_tb = ToggleButton(text='Subtract', group='adjust_mode',
                              allow_no_selection=False)
        set_tb = ToggleButton(text='Set', group='adjust_mode',
                              allow_no_selection=False)
        for tb in (add_tb, sub_tb, set_tb):
            mode_row.add_widget(tb)
        content.add_widget(mode_row)

        # --- Amount entry ---
        amount_input = TextInput(
            hint_text='Amount in J',
            input_filter='float',
            multiline=False,
            size_hint_y=None, height=40
        )
        content.add_widget(amount_input)

        # --- Quick amounts ---
        quick_row = BoxLayout(size_hint_y=None, height=35, spacing=5)
        for amt in (100, 1000, 10000, 100000):
            qb = Button(text=f"{amt:,}")
            qb.bind(on_press=lambda x, a=amt: setattr(amount_input, 'text', str(a)))
            quick_row.add_widget(qb)
        content.add_widget(quick_row)

        status_label = Label(text='', size_hint_y=None, height=25)
        content.add_widget(status_label)

        # --- Actions ---
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=5)
        apply_btn = Button(text='Apply')
        close_btn = Button(text='Close')
        btn_layout.add_widget(apply_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Adjust Balance', content=content,
                      size_hint=(0.85, 0.65))

        def set_status(msg, error=False):
            status_label.text = msg
            status_label.color = (1, 0.3, 0.3, 1) if error else (0.4, 1, 0.4, 1)

        def apply_adjustment(instance):
            raw = amount_input.text.strip()
            if not raw:
                set_status('Enter an amount first.', error=True)
                return
            try:
                amount = abs(float(raw))
            except ValueError:
                set_status('Amount must be a number.', error=True)
                return

            current = self.data_handler.get_user_balance(username)

            if sub_tb.state == 'down':
                mode = 'subtract'
            elif set_tb.state == 'down':
                mode = 'set'
            else:
                mode = 'add'

            if mode == 'add':
                delta = amount
            elif mode == 'subtract':
                delta = -amount
            else:
                delta = amount - current

            if delta == 0:
                set_status('No change needed.')
                return

            # Same guard as DataHandler.add_to_balance, but checked up front
            if delta < 0 and current + delta < 0:
                set_status(f"Insufficient balance: {username} has {current} J.",
                           error=True)
                return

            metadata = {'admin_action': mode, 'previous_balance': current}

            try:
                if delta > 0:
                    self.data_handler.update_balance_with_transaction(
                        None, username, delta,
                        transaction_type='admin_adjust', metadata=metadata
                    )
                else:
                    self.data_handler.update_balance_with_transaction(
                        username, None, abs(delta),
                        transaction_type='admin_adjust', metadata=metadata
                    )
            except Exception as e:
                set_status(f'Error: {e}', error=True)
                return

            new_balance = self.data_handler.get_user_balance(username)
            balance_label.text = f"Balance: {new_balance} J"
            amount_input.text = ''
            set_status(f"Updated: {current} J -> {new_balance} J")
            self.refresh_users()

        apply_btn.bind(on_press=apply_adjustment)
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def show_edit_popup(self, username):
        """Tabbed editor for profile / services / tasks. Each save is hashed + logged."""
        admin_id = self.current_username or "admin"

        tabs = TabbedPanel(do_default_tab=False, size_hint=(1, 1))

        status_label = Label(text='', size_hint_y=None, height=25)

        def add_service(instance):
            open_service_popup(
                self, provider_id=username,
                on_saved=lambda data: save_services(
                    get_services() + [data], 'service_add', {'service': data}
                ),
            )

        def edit_service(idx):
            items = get_services()
            if idx >= len(items):
                return
            original = items[idx]

            def on_saved(data, i=idx):
                current = get_services()
                current[i] = data
                save_services(current, 'service_edit',
                              {'index': i, 'service': data})

            open_service_popup(self, service_data=original, on_saved=on_saved)

        # ---- helper: refresh a list grid in place ----
        def rebuild_grid(grid, items, on_edit, on_delete):
            grid.clear_widgets()
            for i, item in enumerate(items):
                row = BoxLayout(size_hint_y=None, height=55, spacing=4)
                preview = json.dumps(item)
                if len(preview) > 60:
                    preview = preview[:57] + "..."
                row.add_widget(Label(text=preview, size_hint_x=0.6, halign='left',
                                     valign='middle', text_size=(None, None)))
                edit_btn = Button(text='Edit', size_hint_x=0.2)
                edit_btn.bind(on_press=lambda x, idx=i: on_edit(idx))
                del_btn = Button(text='Del', size_hint_x=0.2)
                del_btn.bind(on_press=lambda x, idx=i: on_delete(idx))
                row.add_widget(edit_btn)
                row.add_widget(del_btn)
                grid.add_widget(row)

        # ==================== PROFILE TAB ====================
        profile = self.data_handler.load_user_profile(username)

        profile_tab = TabbedPanelItem(text='Profile')
        profile_box = BoxLayout(orientation='vertical', spacing=6, padding=6)

        profile_box.add_widget(Label(text='Bio:', size_hint_y=None, height=20))
        bio_input = TextInput(text=profile.get('bio', ''), multiline=True,
                              size_hint_y=None, height=90)
        profile_box.add_widget(bio_input)

        admin_row = BoxLayout(size_hint_y=None, height=30)
        admin_row.add_widget(Label(text='Admin:'))
        admin_cb = CheckBox(active=bool(profile.get('admin', False)))
        admin_row.add_widget(admin_cb)
        profile_box.add_widget(admin_row)

        anon_row = BoxLayout(size_hint_y=None, height=30)
        anon_row.add_widget(Label(text='Anonymize:'))
        anon_cb = CheckBox(active=bool(profile.get('anonymize', False)))
        anon_row.add_widget(anon_cb)
        profile_box.add_widget(anon_row)

        pic_row = BoxLayout(size_hint_y=None, height=30, spacing=4)
        pic_row.add_widget(Label(text='Profile Pic:', size_hint_x=0.4))
        pic_input = TextInput(text=profile.get('profile_pic', ''), multiline=False)
        pic_row.add_widget(pic_input)
        profile_box.add_widget(pic_row)

        def save_profile(instance):
            updates = {
                'bio': bio_input.text,
                'admin': admin_cb.active,
                'anonymize': anon_cb.active,
                'profile_pic': pic_input.text,
            }
            self.data_handler.update_user_profile(username, updates)
            entry = self.data_handler.log_admin_action(
                admin_id, username, 'profile_edit',
                {'updated_fields': list(updates.keys())}
            )
            status_label.text = f"Profile saved. Hash: {entry['hash'][:12]}..."

        save_profile_btn = Button(text='Save Profile', size_hint_y=None, height=40)
        save_profile_btn.bind(on_press=save_profile)
        profile_box.add_widget(save_profile_btn)
        profile_tab.add_widget(profile_box)
        tabs.add_widget(profile_tab)

        # ==================== SERVICES TAB ====================
        services_tab = TabbedPanelItem(text='Services')
        services_box = BoxLayout(orientation='vertical', spacing=6, padding=6)

        services_scroll = ScrollView()
        services_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        services_grid.bind(minimum_height=services_grid.setter('height'))
        services_scroll.add_widget(services_grid)
        services_box.add_widget(services_scroll)

        def get_services():
            return self.data_handler.load_user_profile(username).get('services', [])

        def save_services(new_list, action, details):
            self.data_handler.overwrite_services(new_list, user_id=username)
            entry = self.data_handler.log_admin_action(admin_id, username, action, details)
            status_label.text = f"{action} logged. Hash: {entry['hash'][:12]}..."
            rebuild_grid(services_grid, get_services(),
                         edit_service, delete_service)

        def delete_service(idx):
            items = get_services()
            if idx >= len(items):
                return
            removed = items.pop(idx)
            save_services(items, 'service_delete', {'removed': removed})

        add_service_btn = Button(text='+ Add Service', size_hint_y=None, height=40)
        add_service_btn.bind(on_press=add_service)
        services_box.add_widget(add_service_btn)
        services_tab.add_widget(services_box)
        tabs.add_widget(services_tab)

        # ==================== TASKS TAB ====================
        tasks_tab = TabbedPanelItem(text='Tasks')
        tasks_box = BoxLayout(orientation='vertical', spacing=6, padding=6)

        tasks_scroll = ScrollView()
        tasks_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        tasks_grid.bind(minimum_height=tasks_grid.setter('height'))
        tasks_scroll.add_widget(tasks_grid)
        tasks_box.add_widget(tasks_scroll)

        def get_tasks():
            return self.data_handler.load_user_profile(username).get('tasks', [])

        def save_tasks(new_list, action, details):
            # Tasks have no dedicated overwrite helper, so save the whole profile.
            prof = self.data_handler.load_user_profile(username)
            prof['tasks'] = new_list
            self.data_handler.save_user_profile(username, prof)
            entry = self.data_handler.log_admin_action(admin_id, username, action, details)
            status_label.text = f"{action} logged. Hash: {entry['hash'][:12]}..."
            rebuild_grid(tasks_grid, get_tasks(), edit_task, delete_task)

        def add_task(instance):
            TaskFormPopup(
                title=f'Add Task for {username}',
                on_submit=lambda data: save_tasks(
                    get_tasks() + [data], 'task_add', {'task': data}
                ),
            ).open()

        def edit_task(idx):
            items = get_tasks()
            if idx >= len(items):
                return

            def on_save(data, i=idx):
                current = get_tasks()
                current[i] = data
                save_tasks(current, 'task_edit', {'index': i, 'task': data})

            TaskFormPopup(
                title=f'Edit Task for {username}',
                initial_data=items[idx],
                on_submit=on_save,
            ).open()

        def delete_task(idx):
            items = get_tasks()
            if idx >= len(items):
                return
            removed = items.pop(idx)
            save_tasks(items, 'task_delete', {'removed': removed})

        add_task_btn = Button(text='+ Add Task', size_hint_y=None, height=40)
        add_task_btn.bind(on_press=add_task)
        tasks_box.add_widget(add_task_btn)
        tasks_tab.add_widget(tasks_box)
        tabs.add_widget(tasks_tab)

        # ==================== ROOT POPUP ====================
        rebuild_grid(services_grid, get_services(), edit_service, delete_service)
        rebuild_grid(tasks_grid, get_tasks(), edit_task, delete_task)

        close_btn = Button(text='Close', size_hint_y=None, height=40)
        root = BoxLayout(orientation='vertical', spacing=6, padding=6)
        root.add_widget(tabs)
        root.add_widget(status_label)
        root.add_widget(close_btn)

        popup = Popup(title=f'Edit {username}', content=root, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        self.manager.current = 'home'