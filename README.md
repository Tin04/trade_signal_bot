# Trade Signal Bot

A Python-based trading bot with technical analysis capabilities and an interactive GUI interface. The bot provides real-time market analysis, trend predictions, and trading signals based on multiple technical indicators.

## Features
- Real-time stock data monitoring
- Technical Analysis Indicators:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
- Interactive GUI Dashboard
- Customizable Trading Signals
- Trend Prediction System
- Backtesting Capabilities
- Multiple Timeframe Analysis

## Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## User Guide

### Basic Operations
1. **Starting the Bot**:
   - Enter a stock symbol (default: AAPL)
   - Select your preferred timeframe (1m, 5m, 15m, 30m, 1h)
   - Click "Start" to begin monitoring

2. **Switching Stocks**:
   - Enter new stock symbol in the symbol field
   - Click "Switch Stock" button
   - Bot will automatically update all indicators for the new stock

3. **Monitoring Trends**:
   - View current price and technical indicators in real-time
   - Check trend predictions showing direction (UP/DOWN/SIDEWAYS)
   - Monitor trend strength and reasoning
   - Watch MACD chart for visual analysis

### Trading Signals
- The bot generates alerts based on:
  - RSI overbought/oversold conditions
  - MACD crossovers
  - Bollinger Band breakouts
  - Volume-price relationships
- Adjust minimum signal strength (default: 0.3) to filter signals
- Receive pop-up alerts with sound for significant trading signals

### Backtesting
1. Select a start date using the date picker
2. Click "Run Backtest" to analyze historical performance
3. View detailed results including:
   - Total trades
   - Profitable trades
   - Total return
   - Trade history

### Timeframe Selection
Choose from multiple timeframes for analysis:
- 1 minute (1m) - For short-term scalping
- 5 minutes (5m) - For intraday trading
- 15 minutes (15m) - For swing trading
- 30 minutes (30m) - For medium-term analysis
- 1 hour (1h) - For longer-term trends

## Tips for Best Use
- Start with longer timeframes (1h) to identify overall trend
- Use shorter timeframes (1m, 5m) for entry/exit timing
- Monitor trend strength for more reliable signals
- Combine multiple indicators for better confirmation
- Use backtesting to validate strategies before live trading

## Note
This bot is for educational and research purposes only. Always perform your own analysis and risk assessment before making trading decisions.
