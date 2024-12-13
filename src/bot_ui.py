# app UI
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import time
from src import TradingBot  # Add this line

class TradingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Bot Dashboard")
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
                
                current_price = df['Close'].iloc[-1]
                self.price_var.set(f"Current Price: ${current_price:.2f}")
                
                df = self.bot.calculate_signals(df)
                
                # Update indicator values
                self.rsi_var.set(f"RSI: {df['RSI'].iloc[-1]:.2f}")
                self.macd_var.set(f"MACD: {df['MACD'].iloc[-1]:.2f}")
                self.bb_upper_var.set(f"BB Upper: {df['BB_high'].iloc[-1]:.2f}")
                self.bb_lower_var.set(f"BB Lower: {df['BB_low'].iloc[-1]:.2f}")
                
                signal = self.bot.generate_signals(df)
                if signal:
                    self.log(f"{signal} signal generated at price: ${df['Close'].iloc[-1]:.2f}")
                    self.bot.position = not self.bot.position
                
                time.sleep(60)
                
            except Exception as e:
                self.log(f"Error occurred: {e}")
                time.sleep(60)

    def switch_stock(self):
        """Switch to a new stock symbol"""
        new_symbol = self.symbol_var.get().upper()
        if new_symbol != self.bot.symbol:
            self.log(f"Switching from {self.bot.symbol} to {new_symbol}")
            self.bot.symbol = new_symbol
            # Reset all displays
            self.price_var.set("Current Price: --")
            self.rsi_var.set("RSI: --")
            self.macd_var.set("MACD: --")
            self.bb_upper_var.set("BB Upper: --")
            self.bb_lower_var.set("BB Lower: --")
            # Reset position
            self.bot.position = False

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()
