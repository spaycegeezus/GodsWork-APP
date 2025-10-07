import sqlite3
from kivy.uix.recycleview import RecycleView

class SQLiteAdapter(RecycleView):
    def __init__(self, db_path='data/app.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance INTEGER DEFAULT 250000
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            category TEXT,
            description TEXT,
            joules INTEGER,
            weight REAL,
            time_units INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            category TEXT,
            description TEXT,
            value INTEGER,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
        """)
        self.conn.commit()

    def save_task(self, task_data, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
            cursor.execute("""
                INSERT INTO tasks (user_id, timestamp, category, description, joules, weight, time_units)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                task_data.get('timestamp'),
                task_data.get('category'),
                task_data.get('description'),
                task_data.get('joules', 0),
                task_data.get('weight', 0),
                task_data.get('time or units', 0)
            ))
            self.conn.commit()

    def load_tasks(self, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "SELECT timestamp, category, description, joules, weight, time_units FROM tasks WHERE user_id = ?",
                (user_id,))
        else:
            cursor.execute("SELECT timestamp, category, description, joules, weight, time_units FROM tasks")
        rows = cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append({
                "timestamp": row[0],
                "category": row[1],
                "description": row[2],
                "joules": row[3],
                "weight": row[4],
                "time or units": row[5]
            })
        return tasks

    def save_service(self, service_data, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (user_id,))
            cursor.execute("""
                INSERT INTO services (user_id, timestamp, category, description, value)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                service_data.get('timestamp'),
                service_data.get('category'),
                service_data.get('description'),
                service_data.get('value')
            ))
            self.conn.commit()

    def load_services(self, user_id=None):
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute("SELECT timestamp, category, description, value FROM services WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("SELECT timestamp, category, description, value FROM services")

        rows = cursor.fetchall()
        services = []
        for row in rows:
            services.append({
                "timestamp": row[0],
                "category": row[1],
                "description": row[2],
                "value": row[3]
            })
        return services

    def get_user_balance(self, user_id, default=0):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return default

    def set_user_balance(self, user_id, new_balance):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users(user_id, balance) VALUES(?, ?)", (user_id, new_balance))
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        self.conn.commit()
