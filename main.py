import tkinter as tk
from src.bot_ui import TradingBotUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()