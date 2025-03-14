from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from auto_machine import TradingSystem

class TradingBotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Status label
        self.status_label = Label(text='Trading Bot Status: Stopped')
        layout.add_widget(self.status_label)
        
        # Start button
        start_button = Button(
            text='Start Trading',
            size_hint=(1, 0.2),
            on_press=self.start_trading
        )
        layout.add_widget(start_button)
        
        # Stop button
        stop_button = Button(
            text='Stop Trading',
            size_hint=(1, 0.2),
            on_press=self.stop_trading
        )
        layout.add_widget(stop_button)
        
        self.trading_system = None
        return layout
    
    def start_trading(self, instance):
        try:
            self.trading_system = TradingSystem()
            self.status_label.text = 'Trading Bot Status: Running'
            self.trading_system.run()
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
    
    def stop_trading(self, instance):
        if self.trading_system:
            self.trading_system = None
            self.status_label.text = 'Trading Bot Status: Stopped'

if __name__ == '__main__':
    TradingBotApp().run()