from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

# this is gw_screen.py

def get_screens():
    from gw_screen.login import LoginScreen
    from gw_screen.profile import ProfileScreen
    from gw_screen.task import TaskScreen
    from gw_screen.service import ServiceScreen
    from gw_screen.account import AccountScreen
    from gw_screen.signup import SignupScreen
    from gw_screen.ledger_viewer import LedgerViewerScreen
    from gw_screen.home import HomeScreen
    from gw_screen.custom_task_popup import CustomTaskPopup
    from gw_screen.service_task_receipt import ServiceTaskReceiptScreen

    return [
        LoginScreen(name='login'),
        HomeScreen(name='home'),
        ProfileScreen(name='profile'),
        ServiceScreen(name='service'),
        TaskScreen(name='task'),
        SignupScreen(name='signup'),
        AccountScreen(name='account'),
        LedgerViewerScreen(name='ledger'),
        ServiceTaskReceiptScreen(name='service_task_receipt'),
        CustomTaskPopup(name='custom_task_popup')
        # ChatScreen(name='chat') for future addition
        # MessageScreen(name='message')

    ]
