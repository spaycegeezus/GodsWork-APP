import sys
import os
from gw_screen.home import HomeScreen
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from gw_screen.__init__ import init_db
from gw_screen.login import LoginScreen
from gw_screen.profile import ProfileScreen
from gw_screen.task import TaskScreen
from gw_screen.service import ServiceScreen
from gw_screen.account import AccountScreen
from gw_screen.signup import SignupScreen
from gw_screen.custom_task_popup import CustomTaskPopup
from gw_screen.ledger_viewer import LedgerViewerScreen
from dotenv import load_dotenv
from utils.data_handler import DataHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set your desired backend: "json", "sql", or "cassandra"
data = DataHandler(backend="json"),
# -- (backend="sql")
# -- (backend="cassandra");  # Can be made dynamic later
init_db()
load_dotenv()

# This is godswork.py
class GodScreenManager(ScreenManager):
    pass

class GodsWorkApp(App):
    def build(self):
        self.title = "God's Work"
        sm = GodScreenManager(transition=FadeTransition())

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TaskScreen(name='task'))
        sm.add_widget(ServiceScreen(name='service'))
        sm.add_widget(AccountScreen(name='account'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(LedgerViewerScreen(name='ledger_viewer'))
        sm.add_widget(ProfileScreen(name='profile', user_id='anonymous'))


        # sm.add_widget(ChatScreen(name='chat'))
        # sm.add_widget(MessageScreen(name='direct_message'))

        return sm

if __name__ == '__main__':
    GodsWorkApp().run()
