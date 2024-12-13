# core logic
import yfinance as yf
import pandas as pd
import ta
import time
from datetime import datetime
from src.utils.strategies import TradingStrategies, Signal

class TradingBot:
    def __init__(self, symbol, interval='1m'):
        self.symbol = symbol.upper()
        self.interval = interval
        self.position = False  # False = no position, True = has position
        self.strategies = TradingStrategies()
        self.min_signal_strength = 0.3  # Minimum signal strength threshold
        
    @property
    def symbol(self):
        return self._symbol
    
    @symbol.setter
    def symbol(self, new_symbol):
        """Allow changing the symbol after initialization"""
        self._symbol = new_symbol.upper()
    
    def get_data(self):
        """Fetch real-time stock data"""
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(period='1d', interval=self.interval)
            if df.empty:
                raise Exception("No data received from yfinance")
            print(f"Fetched {len(df)} rows of data")  # Debug print
            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_signals(self, df):
        """Calculate technical indicators and generate signals"""
        # Adding RSI
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # Adding MACD
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        
        # Adding Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['BB_high'] = bollinger.bollinger_hband()
        df['BB_low'] = bollinger.bollinger_lband()
        
        return df
    
    def analyze_signals(self, df) -> list[Signal]:
        """Analyze all strategies and return triggered signals"""
        signals = []
        
        # Check each strategy
        strategies = [
            self.strategies.rsi_strategy,
            self.strategies.macd_cross_strategy,
            self.strategies.bollinger_bands_strategy,
            self.strategies.volume_price_strategy
        ]
        
        for strategy in strategies:
            signal = strategy(df)
            if signal and signal.strength >= self.min_signal_strength:
                signals.append(signal)
                
        return signals
    
    def run(self):
        """Main bot loop"""
        print(f"Starting bot for {self.symbol}")
        while True:
            try:
                # Get current data
                df = self.get_data()
                if df is None:
                    print("No data available, waiting before retry...")
                    time.sleep(60)
                    continue
                
                # Print current price for debugging
                current_price = df['Close'].iloc[-1]
                print(f"Current price: ${current_price:.2f}")
                
                # Calculate technical indicators
                df = self.calculate_signals(df)
                
                # Print indicator values for debugging
                print(f"RSI: {df['RSI'].iloc[-1]:.2f}")
                print(f"MACD: {df['MACD'].iloc[-1]:.2f}")
                print(f"BB Upper: {df['BB_high'].iloc[-1]:.2f}")
                print(f"BB Lower: {df['BB_low'].iloc[-1]:.2f}")
                
                # Analyze trading signals
                signals = self.analyze_signals(df)
                
                for signal in signals:
                    print(f"{datetime.now()}: {signal.type} signal generated at price: {signal.price:.2f} ({signal.reason})")
                    self.position = not self.position  # Toggle position
                
                if not signals:
                    print("No trading signal generated")
                
                # Wait before next iteration
                print("Waiting 60 seconds before next check...")
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    # Create and run bot for AAPL (or any other valid symbol)
    bot = TradingBot("ETHT")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"\nBot stopped due to error: {e}")
