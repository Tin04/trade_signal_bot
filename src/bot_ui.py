# app UI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime, timedelta
import time
from src import TradingBot  # Add this line
import winsound  # For Windows alert sound (use different library for other OS)
from src.utils.strategies import Signal  # Add this import
from src.utils.trend_predictor import TrendPredictor  # Add this import
from tkcalendar import DateEntry

class TradingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trade Signal Bot Dashboard")
        self.root.geometry("800x600")
        self.bot = None
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Frame for Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Symbol Input
        ttk.Label(control_frame, text="Symbol:").pack(side=tk.LEFT)
        self.symbol_var = tk.StringVar(value="AAPL")
        self.symbol_entry = ttk.Entry(control_frame, textvariable=self.symbol_var, width=10)
        self.symbol_entry.pack(side=tk.LEFT, padx=5)
        
        # Add Switch Stock Button
        self.switch_button = ttk.Button(control_frame, text="Switch Stock", command=self.switch_stock)
        self.switch_button.pack(side=tk.LEFT, padx=5)
        self.switch_button.config(state='disabled')  # Disabled by default
        
        # Interval Selection
        ttk.Label(control_frame, text="Interval:").pack(side=tk.LEFT, padx=(10,0))
        self.interval_var = tk.StringVar(value="1m")
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                    values=["1m", "5m", "15m", "30m", "1h"], width=5)
        interval_combo.pack(side=tk.LEFT, padx=5)
        
        # Start/Stop Button
        self.start_button = ttk.Button(control_frame, text="Start", command=self.toggle_bot)
        self.start_button.pack(side=tk.LEFT, padx=20)
        
        # Main Data Display Area
        data_frame = ttk.LabelFrame(self.root, text="Real-time Data", padding="10")
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Price and Indicators Display
        self.price_var = tk.StringVar(value="Current Price: --")
        self.rsi_var = tk.StringVar(value="RSI: --")
        self.macd_var = tk.StringVar(value="MACD: --")
        self.bb_upper_var = tk.StringVar(value="BB Upper: --")
        self.bb_lower_var = tk.StringVar(value="BB Lower: --")
        
        ttk.Label(data_frame, textvariable=self.price_var).pack(anchor='w')
        ttk.Label(data_frame, textvariable=self.rsi_var).pack(anchor='w')
        ttk.Label(data_frame, textvariable=self.macd_var).pack(anchor='w')
        ttk.Label(data_frame, textvariable=self.bb_upper_var).pack(anchor='w')
        ttk.Label(data_frame, textvariable=self.bb_lower_var).pack(anchor='w')
        
        # Log Display
        log_frame = ttk.LabelFrame(self.root, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add Strategy Frame
        strategy_frame = ttk.LabelFrame(self.root, text="Strategy Settings", padding="10")
        strategy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add strategy controls
        ttk.Label(strategy_frame, text="Min Signal Strength:").pack(side=tk.LEFT)
        self.signal_strength_var = tk.StringVar(value="0.3")
        signal_strength_entry = ttk.Entry(strategy_frame, textvariable=self.signal_strength_var, width=5)
        signal_strength_entry.pack(side=tk.LEFT, padx=5)
        
        # Add Backtest Frame
        backtest_frame = ttk.LabelFrame(self.root, text="Backtesting", padding="10")
        backtest_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start Date
        ttk.Label(backtest_frame, text="Start Date:").pack(side=tk.LEFT)
        self.start_date_picker = DateEntry(backtest_frame, 
                                         width=12,
                                         background='darkblue',
                                         foreground='white',
                                         borderwidth=2,
                                         date_pattern='yyyy-mm-dd',
                                         maxdate=self.get_last_trading_day(),)  # Use helper method)
        self.start_date_picker.pack(side=tk.LEFT, padx=5)
        
        # Label and entry for initial capital
        ttk.Label(backtest_frame, text="Initial Capital (int):").pack(side=tk.LEFT)
        self.backtest_capital = ttk.Entry(backtest_frame)
        self.backtest_capital.pack(side=tk.LEFT, padx=5)
        self.backtest_capital.insert(0, "10000")  # Default value

        # Run Backtest Button
        self.backtest_button = ttk.Button(backtest_frame, text="Run Backtest", command=self.run_backtest)
        self.backtest_button.pack(side=tk.LEFT, padx=20)
        
        # Add Trend Prediction Frame
        trend_frame = ttk.LabelFrame(self.root, text="Trend Prediction", padding="10")
        trend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add prediction labels
        self.trend_direction_var = tk.StringVar(value="Direction: --")
        self.trend_strength_var = tk.StringVar(value="Strength: --")
        self.trend_reason_var = tk.StringVar(value="Reason: --")
        
        ttk.Label(trend_frame, textvariable=self.trend_direction_var, font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Label(trend_frame, textvariable=self.trend_strength_var).pack(anchor='w')
        ttk.Label(trend_frame, textvariable=self.trend_reason_var).pack(anchor='w')

    def get_last_trading_day(self):
        """Return the last trading day (excluding weekends)"""
        today = datetime.now()
        # If today is Sunday, subtract 2 days
        if today.weekday() == 6:
            return today - timedelta(days=2)
        # If today is Saturday, subtract 1 day
        elif today.weekday() == 5:
            return today - timedelta(days=1)
        return today

    def log(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
        self.log_text.see(tk.END)
        
    def toggle_bot(self):
        if not self.is_running:
            self.start_bot()
        else:
            self.stop_bot()
            
    def start_bot(self):
        self.is_running = True
        self.start_button.config(text="Stop")
        self.switch_button.config(state='normal')  # Enable switch button when bot starts
        self.log("Bot started")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        
    def stop_bot(self):
        self.is_running = False
        self.start_button.config(text="Start")
        self.switch_button.config(state='disabled')  # Disable switch button when bot stops
        self.log("Bot stopped")
        
    def run_bot(self):
        self.bot = TradingBot(self.symbol_var.get(), self.interval_var.get())
        
        while self.is_running:
            try:
                df = self.bot.get_data()
                if df is None:
                    self.log("No data available, waiting before retry...")
                    time.sleep(60)
                    continue
                
                # Calculate indicators
                df = self.bot.calculate_signals(df)
                
                # Update regular displays
                current_price = df['Close'].iloc[-1]
                self.price_var.set(f"Current Price: ${current_price:.2f}")
                self.rsi_var.set(f"RSI: {df['RSI'].iloc[-1]:.2f}")
                self.macd_var.set(f"MACD: {df['MACD'].iloc[-1]:.2f}")
                self.bb_upper_var.set(f"BB Upper: {df['BB_high'].iloc[-1]:.2f}")
                self.bb_lower_var.set(f"BB Lower: {df['BB_low'].iloc[-1]:.2f}")
                
                # Get and display trend prediction
                direction, strength, reason = TrendPredictor.predict_trend(df)
                
                # Update prediction displays with colors
                self.trend_direction_var.set(f"Direction: {direction}")
                self.trend_strength_var.set(f"Strength: {strength:.2f}")
                self.trend_reason_var.set(f"Reason: {reason}")
                
                # Color-code the direction based on prediction
                color = {
                    "UP": "green",
                    "DOWN": "red",
                    "SIDEWAYS": "gray"
                }.get(direction, "black")
                
                # Log significant trend changes
                self.log(f"Trend Update: {direction} (Strength: {strength:.2f}) - {reason}")
                
                # Check for signals
                signals = self.bot.analyze_signals(df)
                for signal in signals:
                    self.show_alert(signal)
                
                time.sleep(60)
                
            except Exception as e:
                self.log(f"Error occurred: {e}")
                time.sleep(60)

    def switch_stock(self):
        """Switch to a new stock symbol"""
        new_symbol = self.symbol_var.get().upper()
        if new_symbol != self.bot.symbol:
            self.log(f"Switching from {self.bot.symbol} to {new_symbol}")
            
            # Create a new bot instance (same as starting)
            self.bot = TradingBot(new_symbol, self.interval_var.get())
            
            try:
                # Get and process data
                df = self.bot.get_data()
                if df is not None:
                    df = self.bot.calculate_signals(df)
                    
                    # Update all displays
                    current_price = df['Close'].iloc[-1]
                    self.price_var.set(f"Current Price: ${current_price:.2f}")
                    self.rsi_var.set(f"RSI: {df['RSI'].iloc[-1]:.2f}")
                    self.macd_var.set(f"MACD: {df['MACD'].iloc[-1]:.2f}")
                    self.bb_upper_var.set(f"BB Upper: {df['BB_high'].iloc[-1]:.2f}")
                    self.bb_lower_var.set(f"BB Lower: {df['BB_low'].iloc[-1]:.2f}")
                    
                    # Get trend prediction
                    direction, strength, reason = TrendPredictor.predict_trend(df)
                    self.trend_direction_var.set(f"Direction: {direction}")
                    self.trend_strength_var.set(f"Strength: {strength:.2f}")
                    self.trend_reason_var.set(f"Reason: {reason}")
                    
                    # Check for signals
                    signals = self.bot.analyze_signals(df)
                    for signal in signals:
                        self.show_alert(signal)
                        
                    self.log(f"Successfully switched to {new_symbol}")
                    
                    # Log significant trend changes
                    self.log(f"Trend Update: {direction} (Strength: {strength:.2f}) - {reason}")
                else:
                    self.log(f"Error: Could not fetch data for {new_symbol}")
            except Exception as e:
                self.log(f"Error switching to {new_symbol}: {e}")

    def show_alert(self, signal: Signal):
        """Show alert for trading signal"""
        message = f"""
        {signal.type} Signal Detected!
        Price: ${signal.price:.2f}
        Reason: {signal.reason}
        Strength: {signal.strength:.2f}
        """
        
        # Play alert sound
        winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        
        # Show popup
        messagebox.showinfo("Trading Signal", message)
        
        # Log signal
        self.log(f"Signal: {signal.type} - {signal.reason} (Strength: {signal.strength:.2f})")

    def validate_symbol(self, symbol):
        """Validate if the symbol exists with more detailed checking"""
        import yfinance as yf
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period="5d")
            if hist.empty:
                self.log(f"No historical data found for {symbol}")
                return False
                
            # Check if it's a valid ticker by ensuring basic info exists
            info = ticker.info
            if not info:
                self.log(f"No information available for {symbol}")
                return False
                
            # Additional checks if needed
            if 'regularMarketPrice' not in info and 'previousClose' not in info:
                self.log(f"No price information available for {symbol}")
                return False
                
            return True
            
        except Exception as e:
            self.log(f"Symbol validation error: {e}")
            return False
    
    def run_backtest(self):
        """Run backtest with current settings"""
        try:
            from .utils.backtester import Backtester
            
            symbol = self.symbol_var.get()
                        
            # Check if symbol exist
            if not self.validate_symbol(symbol):
                messagebox.showerror("Error", f"Invalid symbol or no data available for {symbol}")
                return
            
            backtest_capital = int(self.backtest_capital.get())  # Convert to integer
            if backtest_capital <= 0:
                raise ValueError("Capital must be a positive integer.")
            
            start_date = self.start_date_picker.get_date()

            # Check if start_date is a weekend
            if start_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
                messagebox.showerror("Error", "Please select a weekday for backtesting")
                return
        
            self.log(f"Starting backtest for {symbol} from {start_date}")
            
            backtester = Backtester(symbol, start_date, initial_capital=backtest_capital)
            results = backtester.run_backtest()
            
            if results:
                # Show results in a new window
                results_window = tk.Toplevel(self.root)
                results_window.title("Backtest Results")
                results_window.geometry("600x400")
                
                # Results text
                results_text = scrolledtext.ScrolledText(results_window, height=20)
                results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Format results
                results_text.insert(tk.END, f"Backtest Results for {symbol}\n")
                results_text.insert(tk.END, f"Period: {start_date} to {datetime.now().date()}\n\n")
                results_text.insert(tk.END, f"Total Trades: {results['total_trades']}\n")
                results_text.insert(tk.END, f"Profitable Trades: {results['profitable_trades']}\n")
                results_text.insert(tk.END, f"Total Return: ${results['total_return']:.2f}\n")
                results_text.insert(tk.END, f"Return %: {results['return_pct']:.2f}%\n\n")
                
                results_text.insert(tk.END, "Trade History:\n")
                for trade in results['trades']:
                    results_text.insert(tk.END, 
                        f"{trade['date']}: {trade['type']} {trade['shares']} shares @ ${trade['price']:.2f}\n"
                        f"    Reason: {trade['reason']}\n"
                        f"    Capital: ${trade['capital']:.2f}\n\n"
                    )
                
                results_text.config(state='disabled')
                
            else:
                messagebox.showerror("Error", "No backtest results available")
        
        except ValueError as v:
            messagebox.showerror("Invalid Input", f"Please enter a valid integer for initial capital.\n{str(v)}")
            return  # Exit the method if input is invalid
           
        except Exception as e:
            messagebox.showerror("Error", f"Backtest failed: {str(e)}")
            self.log(f"Backtest error: {e}")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()
