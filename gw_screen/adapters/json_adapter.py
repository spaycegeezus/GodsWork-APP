# json_adapter.py
import os
import json

ANON_FILE = "data/anonymous_data.json"
USER_FILE = "data/user_data.json"

class JSONAdapter:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        for file in [ANON_FILE, USER_FILE]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump({}, f)

    def _load_data(self, file, user_id=None):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                return self._validate_structure(data, user_id)
        except (FileNotFoundError, json.JSONDecodeError):
            return (
                {user_id: {"tasks": [], "services": [], "balance": 250000}}
                if user_id
                else {"tasks": [], "services": []}
            )

    def _save_data(self, file, data):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    def _validate_structure(self, data, user_id=None):
        if user_id:
            if not isinstance(data.get(user_id), dict):
                data[user_id] = {"tasks": [], "services": [], "balance": 250000}
            else:
                data[user_id].setdefault("tasks", [])
                data[user_id].setdefault("services", [])
                data[user_id].setdefault("balance", 250000)
        else:
            if not isinstance(data, dict):
                return {"tasks": [], "services": []}
            data.setdefault("tasks", [])
            data.setdefault("services", [])
        return data

    # -------- Tasks --------
    def save_task(self, task_data, user_id=None):
        file = USER_FILE if user_id else ANON_FILE
        data = self._load_data(file, user_id)
        if user_id:
            data[user_id]["tasks"].append(task_data)
        else:
            data["tasks"].append(task_data)
        self._save_data(file, data)

    def load_tasks(self, user_id=None):
        file = USER_FILE if user_id else ANON_FILE
        data = self._load_data(file, user_id)
        return data.get(user_id, {}).get("tasks", []) if user_id else data["tasks"]

    # -------- Services --------
    def save_service(self, service_data, user_id=None):
        file = USER_FILE if user_id else ANON_FILE
        data = self._load_data(file, user_id)
        if user_id:
            data[user_id]["services"].append(service_data)
        else:
            data["services"].append(service_data)
        self._save_data(file, data)

    def load_services(self, user_id=None):
        file = USER_FILE if user_id else ANON_FILE
        data = self._load_data(file, user_id)
        return data.get(user_id, {}).get("services", []) if user_id else data["services"]

    # -------- Balance --------
    def get_user_balance(self, user_id, default=0):
        data = self._load_data(USER_FILE, user_id)
        return data.get(user_id, {}).get("balance", default)

    def set_user_balance(self, user_id, new_balance):
        data = self._load_data(USER_FILE, user_id)
        if user_id not in data:
            data[user_id] = {"tasks": [], "services": [], "balance": 250000}
        data[user_id]["balance"] = new_balance
        self._save_data(USER_FILE, data)
