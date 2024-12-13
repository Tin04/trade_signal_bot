# You can initialize package-wide variables
VERSION = '1.0.0'

# Import commonly used classes to make them easier to import elsewhere
from .bot import TradingBot
from .bot_ui import TradingBotUI

# This allows users to do:
# from src import TradingBot
# Instead of:
# from src.bot import TradingBot 