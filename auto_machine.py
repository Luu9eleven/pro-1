import numpy as np
import pandas as pd
try:
    import MetaTrader5 as mt5
except ImportError:
    raise ImportError("Please install MetaTrader5 package using: pip install MetaTrader5")
from datetime import datetime, timezone
try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense
except ImportError:
    raise ImportError("Please install tensorflow package using: pip install tensorflow")

class TradingSystem:
    def __init__(self):
        # XM Global Markets Settings
        self.xm_server = "XMGlobal-MT5 01"
        self.account = 12345678  # Replace with your XM account number
        self.password = "your_password"  # Replace with your XM password
        
        # Trading Parameters
        self.symbols = ["NASDAQ", "US30", "US500", "GOLD"]
        self.fast_sma_period = 10
        self.slow_sma_period = 50
        self.risk_percent = 1.0
        self.magic_number = 123456
        
        # Initialize XM MT5 Connection
        if not self.initialize_xm_connection():
            raise Exception("XM MT5 initialization failed")
        
        # Initialize LSTM model
        self.model = self._create_model()
        
    def initialize_xm_connection(self):
        if not mt5.initialize(
            server=self.xm_server,
            login=self.account,
            password=self.password
        ):
            print(f"MT5 initialization failed: {mt5.last_error()}")
            return False
            
        if not mt5.connected():
            print("MT5 not connected")
            return False
            
        print(f"Connected to XM Global Markets - Account: {self.account}")
        return True

    def get_xm_symbols(self):
        symbols = mt5.symbols_get()
        if symbols is None:
            print("No symbols found")
            return []
        return [sym.name for sym in symbols]

    # Modified get_historical_data method
    def get_historical_data(self, symbol):
        timeframe = mt5.TIMEFRAME_M1
        date_from = datetime(2020, 1, 1, tzinfo=timezone.utc)
        date_to = datetime.now(timezone.utc)
        
        if not mt5.symbol_select(symbol, True):
            print(f"Symbol {symbol} selection failed")
            return None
        
        rates = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
        if rates is None:
            print(f"Failed to get data for {symbol}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    # Modified run method
    def run(self):
        try:
            # Verify available symbols
            available_symbols = self.get_xm_symbols()
            self.symbols = [s for s in self.symbols if s in available_symbols]
            
            if not self.symbols:
                raise Exception("No valid symbols found")
                
            print(f"Trading on symbols: {self.symbols}")
            
            # Continue with model training and trading
            for symbol in self.symbols:
                print(f"Training model for {symbol}...")
                self.train_model(symbol)
                
            while True:
                for symbol in self.symbols:
                    data = self.get_historical_data(symbol)
                    if data is None:
                        continue
                        
                    processed_data = self.preprocess_data(data)
                    has_buy, has_sell = self.check_positions(symbol)
                    
                    # Get both SMA and LSTM signals
                    sma_signal = 1 if processed_data['SMA_10'].iloc[-1] > processed_data['SMA_50'].iloc[-1] else -1
                    
                    features = processed_data[['close', 'SMA_10', 'SMA_50', 'high', 'low']].values[-100:]
                    lstm_signal = self.model.predict(features.reshape(1, 100, 5))[0][0]
                    
                    # Combined signal with additional checks
                    if sma_signal > 0 and lstm_signal > 0 and not has_buy:
                        self.close_positions(symbol, mt5.POSITION_TYPE_SELL)
                        self.open_position(symbol, mt5.ORDER_TYPE_BUY)
                    elif sma_signal < 0 and lstm_signal < 0 and not has_sell:
                        self.close_positions(symbol, mt5.POSITION_TYPE_BUY)
                        self.open_position(symbol, mt5.ORDER_TYPE_SELL)
                        
                    mt5.sleep(1000)
                    
        except KeyboardInterrupt:
            print("Stopping trading system...")
        finally:
            mt5.shutdown()

# ... rest of the code remains the same ...
