from dataclasses import dataclass
from typing import Optional

@dataclass
class Signal:
    type: str  # 'BUY' or 'SELL'
    price: float
    reason: str
    strength: float  # 0-1 signal strength

class TradingStrategies:
    @staticmethod
    def rsi_strategy(df, rsi_buy=35, rsi_sell=65) -> Optional[Signal]:
        """RSI Strategy: Oversold/Overbought"""
        current_rsi = df['RSI'].iloc[-1]
        price = df['Close'].iloc[-1]
        
        print(f"Current RSI: {current_rsi}")
        
        if current_rsi < rsi_buy:
            strength = 1 - (current_rsi / rsi_buy)
            return Signal('BUY', price, f'RSI oversold: {current_rsi:.2f}', strength)
        elif current_rsi > rsi_sell:
            strength = (current_rsi - rsi_sell) / (100 - rsi_sell)
            return Signal('SELL', price, f'RSI overbought: {current_rsi:.2f}', strength)
        return None

    @staticmethod
    def macd_cross_strategy(df) -> Optional[Signal]:
        """MACD Crossover Strategy"""
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
        """Bollinger Bands Strategy"""
        price = df['Close'].iloc[-1]
        upper_band = df['BB_high'].iloc[-1]
        lower_band = df['BB_low'].iloc[-1]
        
        print(f"Price: {price:.2f}, BB Upper: {upper_band:.2f}, BB Lower: {lower_band:.2f}")
        
        band_margin = 0.005
        if price < lower_band * (1 + band_margin):
            strength = (lower_band - price) / lower_band
            return Signal('BUY', price, 'Price near lower Bollinger Band', strength)
        elif price > upper_band * (1 - band_margin):
            strength = (price - upper_band) / upper_band
            return Signal('SELL', price, 'Price near upper Bollinger Band', strength)
        return None

    @staticmethod
    def volume_price_strategy(df) -> Optional[Signal]:
        """Volume-Price Divergence Strategy"""
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