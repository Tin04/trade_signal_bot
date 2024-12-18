from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import ta
from .strategies import Signal, TradingStrategies

class Backtester:
    def __init__(self, symbol, start_date, end_date=None, initial_capital=10000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date or datetime.now()
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # Number of shares held
        self.trades = []
        self.strategies = TradingStrategies()
    
    def get_historical_data(self, interval='1d'):
        """Fetch historical data for backtesting"""
        ticker = yf.Ticker(self.symbol)
        df = ticker.history(start=self.start_date, end=self.end_date, interval=interval)
        return df
    
    def analyze_signals(self, df) -> list:
        """Analyze all strategies and return triggered signals"""
        signals = []
        
        # Existing strategies
        rsi_signal = TradingStrategies.rsi_strategy(df)
        if rsi_signal:
            signals.append(rsi_signal)
            
        macd_signal = TradingStrategies.macd_cross_strategy(df)
        if macd_signal:
            signals.append(macd_signal)
            
        bb_signal = TradingStrategies.bollinger_bands_strategy(df)
        if bb_signal:
            signals.append(bb_signal)
            
        # Add swing trade strategy
        swing_signal = TradingStrategies.swing_trade_strategy(df)
        if swing_signal:
            signals.append(swing_signal)
        
        return signals
    
    def run_backtest(self, interval='1d'):
        """Run backtest and return performance metrics"""
        try:
            print(f"Starting backtest for {self.symbol} from {self.start_date}")
            df = self.get_historical_data(interval)
            if df.empty:
                return None
            
            # Calculate technical indicators
            df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
            macd = ta.trend.MACD(df['Close'])
            df['MACD'] = macd.macd()
            df['MACD_signal'] = macd.macd_signal()
            bollinger = ta.volatility.BollingerBands(df['Close'])
            df['BB_high'] = bollinger.bollinger_hband()
            df['BB_low'] = bollinger.bollinger_lband()
            
            results = []
            for i in range(len(df)):
                current_data = df.iloc[:i+1]
                if len(current_data) < 20:  # Need enough data for indicators
                    continue
                    
                signals = self.analyze_signals(current_data)
                price = current_data['Close'].iloc[-1]
                date = current_data.index[-1]
                
                for signal in signals:
                    if signal.type == 'BUY' and self.position == 0:
                        # Calculate position size (invest 95% of capital)
                        shares = int((self.capital * 0.95) / price)
                        cost = shares * price
                        self.capital -= cost
                        self.position = shares
                        self.trades.append({
                            'date': date,
                            'type': 'BUY',
                            'price': price,
                            'shares': shares,
                            'cost': cost,
                            'capital': self.capital,
                            'reason': signal.reason
                        })
                        
                    elif signal.type == 'SELL' and self.position > 0:
                        # Sell all shares
                        revenue = self.position * price
                        self.capital += revenue
                        self.trades.append({
                            'date': date,
                            'type': 'SELL',
                            'price': price,
                            'shares': self.position,
                            'revenue': revenue,
                            'capital': self.capital,
                            'reason': signal.reason
                        })
                        self.position = 0
            
            return self.calculate_metrics()
        
        except Exception as e:
            print(f"Backtest error: {e}")
            return None
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'total_return': 0,
                'return_pct': 0,
                'trades': []
            }
        
        profitable_trades = 0
        for i in range(0, len(self.trades) - 1, 2):
            if i + 1 < len(self.trades):
                buy = self.trades[i]
                sell = self.trades[i + 1]
                profit = sell['revenue'] - buy['cost']
                if profit > 0:
                    profitable_trades += 1
        
        final_capital = self.capital + (self.position * self.trades[-1]['price'] if self.position > 0 else 0)
        total_return = final_capital - self.initial_capital
        return_pct = (total_return / self.initial_capital) * 100
        
        return {
            'total_trades': len(self.trades) // 2,
            'profitable_trades': profitable_trades,
            'total_return': total_return,
            'return_pct': return_pct,
            'trades': self.trades
        }