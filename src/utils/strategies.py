from dataclasses import dataclass
from typing import Optional

@dataclass
class Signal:
    type: str  # 'BUY' or 'SELL'
    price: float
    reason: str
    strength: float  # 0-1 signal strength

class TradingStrategies:
    """
    Collection of trading strategies using various technical indicators.
    Each strategy returns a Signal object when conditions are met, or None.
    Signal strength ranges from 0 (weakest) to 1 (strongest).
    """
    
    @staticmethod
    def rsi_strategy(df, rsi_buy=35, rsi_sell=65) -> Optional[Signal]:
        """
        RSI (Relative Strength Index) Strategy
        
        Conditions:
        - BUY when RSI < 35 (oversold condition)
        - SELL when RSI > 65 (overbought condition)
        
        Signal Strength:
        - For BUY: Higher strength when RSI is lower (more oversold)
        - For SELL: Higher strength when RSI is higher (more overbought)
        
        RSI ranges from 0 to 100:
        - Below 30: Typically considered oversold
        - Above 70: Typically considered overbought
        """
        current_rsi = df['RSI'].iloc[-1]
        price = df['Close'].iloc[-1]
        
        print(f"Current RSI: {current_rsi}")
        
        if current_rsi < rsi_buy:
            strength = 1 - (current_rsi / rsi_buy)  # Stronger signal when RSI is lower
            return Signal('BUY', price, f'RSI oversold: {current_rsi:.2f}', strength)
        elif current_rsi > rsi_sell:
            strength = (current_rsi - rsi_sell) / (100 - rsi_sell)  # Stronger signal when RSI is higher
            return Signal('SELL', price, f'RSI overbought: {current_rsi:.2f}', strength)
        return None

    @staticmethod
    def macd_cross_strategy(df) -> Optional[Signal]:
        """
        MACD (Moving Average Convergence Divergence) Crossover Strategy
        
        Components:
        - MACD Line: Difference between 12-day and 26-day EMAs
        - Signal Line: 9-day EMA of MACD Line
        - Histogram: MACD Line - Signal Line
        
        Conditions:
        - BUY when MACD crosses above Signal line (bullish crossover)
        - SELL when MACD crosses below Signal line (bearish crossover)
        
        Signal Strength:
        - Based on the distance between MACD and Signal lines
        - Larger separation indicates stronger trend momentum
        """
        if len(df) < 2:
            return None
            
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_signal'].iloc[-1]
        prev_macd = df['MACD'].iloc[-2]
        prev_signal = df['MACD_signal'].iloc[-2]
        price = df['Close'].iloc[-1]
        
        print(f"MACD: {current_macd:.2f}, Signal: {current_signal:.2f}")
        
        if (prev_macd <= prev_signal and current_macd > current_signal):
            strength = min(1.0, abs(current_macd - current_signal))
            return Signal('BUY', price, 'MACD bullish crossover', strength)
        elif (prev_macd >= prev_signal and current_macd < current_signal):
            strength = min(1.0, abs(current_macd - current_signal))
            return Signal('SELL', price, 'MACD bearish crossover', strength)
        return None

    @staticmethod
    def bollinger_bands_strategy(df) -> Optional[Signal]:
        """
        Bollinger Bands Strategy
        
        Components:
        - Upper Band: 20-day SMA + (2 × 20-day standard deviation)
        - Middle Band: 20-day SMA
        - Lower Band: 20-day SMA - (2 × 20-day standard deviation)
        
        Conditions:
        - BUY when price touches or crosses below lower band (potential support)
        - SELL when price touches or crosses above upper band (potential resistance)
        
        Signal Strength:
        - Based on how far price has moved beyond the bands
        - Uses 0.5% margin to detect band touches
        """
        price = df['Close'].iloc[-1]
        upper_band = df['BB_high'].iloc[-1]
        lower_band = df['BB_low'].iloc[-1]
        
        print(f"Price: {price:.2f}, BB Upper: {upper_band:.2f}, BB Lower: {lower_band:.2f}")
        
        band_margin = 0.005  # 0.5% margin for band touches
        if price < lower_band * (1 + band_margin):
            strength = (lower_band - price) / lower_band
            return Signal('BUY', price, 'Price near lower Bollinger Band', strength)
        elif price > upper_band * (1 - band_margin):
            strength = (price - upper_band) / upper_band
            return Signal('SELL', price, 'Price near upper Bollinger Band', strength)
        return None

    @staticmethod
    def volume_price_strategy(df) -> Optional[Signal]:
        """
        Volume-Price Divergence Strategy
        
        Concept:
        - Volume often precedes price movement
        - High volume moves are more significant than low volume moves
        
        Conditions:
        - BUY when volume spikes (>1.5x 20-day average) with price increase
        - SELL when volume spikes (>1.5x 20-day average) with price decrease
        
        Signal Strength:
        - Based on how much volume exceeds the average
        - Higher volume = stronger signal
        
        Note: Requires at least 20 days of data for moving average calculation
        """
        if len(df) < 20:
            return None
            
        current_volume = df['Volume'].iloc[-1]
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
        price = df['Close'].iloc[-1]
        
        print(f"Volume: {current_volume}, Avg Volume: {avg_volume}")
        
        if current_volume > 1.5 * avg_volume:
            price_change = (price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]
            if price_change > 0:
                return Signal('BUY', price, 'High volume price increase', min(1.0, current_volume/avg_volume - 1))
            elif price_change < 0:
                return Signal('SELL', price, 'High volume price decrease', min(1.0, current_volume/avg_volume - 1))
        return None