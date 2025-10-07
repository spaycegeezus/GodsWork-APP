from kivy import ABC


class BaseAdapter(ABC):

    @abstractmethod
    def save_task(self, task_data, user_id=None):
        pass

    @abstractmethod
    def load_tasks(self, user_id=None):
        pass

    @abstractmethod
    def save_service(self, service_data, user_id=None):
        pass

    @abstractmethod
    def load_services(self, user_id=None):
        pass

    @abstractmethod
    def get_user_balance(self, user_id, default=0):
        pass

    @abstractmethod
    def set_user_balance(self, user_id, new_balance):
        pass

    # Add more methods here as needed, for profiles, logs, etc.



