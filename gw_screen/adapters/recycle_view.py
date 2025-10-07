from kivy.uix.recycleview import RecycleView
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class MyRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(MyRecycleView, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(20)]  # or load from JSON

class MyBox(BoxLayout):
    pass

class TestApp(App):
    def build(self):
        return MyRecycleView()

if __name__ == '__main__':
    TestApp().run()
