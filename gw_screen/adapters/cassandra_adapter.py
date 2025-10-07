# cassandra_adapter.py

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime
from kivy.uix.recycleview import RecycleView

KEYSPACE = "joules_app"

class CassandraAdapter(RecycleView):
    def __init__(self, keyspace=KEYSPACE):
        self.cluster = Cluster()
        self.session = self.cluster.connect()
        self._ensure_keyspace(keyspace)
        self.session.set_keyspace(keyspace)
        self._create_tables()

    def _ensure_keyspace(self, keyspace):
        self.session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
        """)

    def _create_tables(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                balance BIGINT
            )
        """)
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                user_id TEXT,
                timestamp TEXT,
                category TEXT,
                description TEXT,
                joules INT,
                weight DOUBLE,
                time_units INT,
                PRIMARY KEY (user_id, timestamp)
            )
        """)
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS services (
                user_id TEXT,
                timestamp TEXT,
                category TEXT,
                description TEXT,
                value INT,
                PRIMARY KEY (user_id, timestamp)
            )
        """)

    def save_task(self, task_data, user_id=None):
        query = SimpleStatement("""
            INSERT INTO tasks (user_id, timestamp, category, description, joules, weight, time_units)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """)
        timestamp = task_data.get('timestamp') or datetime.utcnow().isoformat()
        self.session.execute(query, (
            user_id,
            timestamp,
            task_data.get('category'),
            task_data.get('description'),
            task_data.get('joules', 0),
            task_data.get('weight', 0.0),
            task_data.get('time or units', 0)
        ))

    def load_tasks(self, user_id=None):
        query = "SELECT * FROM tasks"
        if user_id:
            query += f" WHERE user_id = '{user_id}'"
        rows = self.session.execute(query)
        return [
            {
                "user_id": row.user_id,
                "timestamp": row.timestamp,
                "category": row.category,
                "description": row.description,
                "joules": row.joules,
                "weight": row.weight,
                "time or units": row.time_units
            }
            for row in rows
        ]

    def save_service(self, service_data, user_id=None):
        query = SimpleStatement("""
            INSERT INTO services (user_id, timestamp, category, description, value)
            VALUES (%s, %s, %s, %s, %s)
        """)
        timestamp = service_data.get('timestamp') or datetime.utcnow().isoformat()
        self.session.execute(query, (
            user_id,
            timestamp,
            service_data.get('category'),
            service_data.get('description'),
            service_data.get('value')
        ))

    def load_services(self, user_id=None):
        query = "SELECT * FROM services"
        if user_id:
            query += f" WHERE user_id = '{user_id}'"
        rows = self.session.execute(query)
        return [
            {
                "user_id": row.user_id,
                "timestamp": row.timestamp,
                "category": row.category,
                "description": row.description,
                "value": row.value
            }
            for row in rows
        ]

    def get_user_balance(self, user_id, default=0):
        result = self.session.execute("SELECT balance FROM users WHERE user_id = %s", [user_id]).one()
        return result.balance if result and result.balance is not None else default

    def set_user_balance(self, user_id, new_balance):
        self.session.execute("""
            INSERT INTO users (user_id, balance) VALUES (%s, %s)
        """, (user_id, new_balance))
