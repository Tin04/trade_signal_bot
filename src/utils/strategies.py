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

    @staticmethod
    def find_support_resistance(df, window=20, threshold=0.02):
        """
        Find support and resistance levels using price pivots and volume.
        
        Parameters:
        - window: lookback period for finding pivots
        - threshold: minimum price difference (%) to consider a new level
        
        Returns:
        - support_levels: list of support prices
        - resistance_levels: list of resistance prices
        """
        highs = df['High'].values
        lows = df['Low'].values
        volumes = df['Volume'].values
        
        support_levels = []
        resistance_levels = []
        
        # Find pivot points
        for i in range(window, len(df) - window):
            # Potential support
            if all(lows[i] <= lows[i-window:i]) and all(lows[i] <= lows[i+1:i+window]):
                # Confirm with volume
                if volumes[i] > volumes[i-window:i+window].mean():
                    support_levels.append(lows[i])
                    
            # Potential resistance
            if all(highs[i] >= highs[i-window:i]) and all(highs[i] >= highs[i+1:i+window]):
                # Confirm with volume
                if volumes[i] > volumes[i-window:i+window].mean():
                    resistance_levels.append(highs[i])
        
        # Cluster nearby levels
        def cluster_levels(levels, threshold):
            if not levels:
                return []
            levels = sorted(levels)
            clustered = []
            current_cluster = [levels[0]]
            
            for level in levels[1:]:
                if (level - current_cluster[0]) / current_cluster[0] <= threshold:
                    current_cluster.append(level)
                else:
                    clustered.append(sum(current_cluster) / len(current_cluster))
                    current_cluster = [level]
            
            if current_cluster:
                clustered.append(sum(current_cluster) / len(current_cluster))
            return clustered
        
        support_levels = cluster_levels(support_levels, threshold)
        resistance_levels = cluster_levels(resistance_levels, threshold)
        
        return support_levels, resistance_levels

    @staticmethod
    def swing_trade_strategy(df) -> Optional[Signal]:
        """
        Enhanced Swing Trading Strategy with dynamic support/resistance.
        
        This strategy identifies potential swing trade opportunities based on:
        - Support and resistance levels
        - Trend strength
        - Volume confirmation
        - Price action patterns
        
        Conditions:
        - BUY when:
            1. Price bounces off support with increased volume
            2. Upward trend confirmation (higher lows)
            3. RSI showing oversold but starting to rise
        
        - SELL when:
            1. Price hits resistance with increased volume
            2. Downward trend confirmation (lower highs)
            3. RSI showing overbought and starting to fall
        
        Signal Strength:
        - Based on multiple confirmations
        - Volume surge adds to strength
        - Clear support/resistance levels increase strength
        """
        try:
            # Ensure there is enough data for analysis
            if len(df) < 20:
                return None
                
            # Get the current price and volume
            current_price = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
            rsi = df['RSI'].iloc[-1]
            prev_rsi = df['RSI'].iloc[-2]
            
            # Find support and resistance levels
            support_levels, resistance_levels = TradingStrategies.find_support_resistance(df)
            
            # Ensure we have valid support and resistance levels
            if not support_levels or not resistance_levels:
                return None
                
            # Find the nearest support and resistance levels
            nearest_support = max([s for s in support_levels if s < current_price], default=None)
            nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
            
            # Ensure we have valid nearest levels
            if not nearest_support or not nearest_resistance:
                return None
                
            # Calculate price distances to support and resistance
            support_distance = (current_price - nearest_support) / nearest_support
            resistance_distance = (nearest_resistance - current_price) / current_price
            
            # Check for volume confirmation (surge)
            volume_surge = current_volume > (1.5 * avg_volume)
            
            # Trend confirmation using recent lows and highs
            last_5_lows = df['Low'].rolling(window=5).min()
            last_5_highs = df['High'].rolling(window=5).max()
            higher_lows = last_5_lows.iloc[-1] > last_5_lows.iloc[-5]  # Check for higher lows
            lower_highs = last_5_highs.iloc[-1] < last_5_highs.iloc[-5]  # Check for lower highs
            
            # BUY Signal Conditions
            if (support_distance < 0.02  # Price near support (2% threshold)
                and higher_lows  # Confirm upward trend
                and rsi < 40 and rsi > prev_rsi):  # RSI oversold but rising
                
                # Calculate signal strength factors
                strength_factors = [
                    0.3,  # Base strength
                    0.2 if volume_surge else 0,  # Add strength if volume surges
                    0.3 if rsi < 30 else 0.1,  # Add strength if RSI is very low
                    0.2 * (1 - support_distance/0.02)  # Proximity to support increases strength
                ]
                
                strength = min(1.0, sum(strength_factors))  # Calculate total strength
                reason = f"Swing Trade BUY: Near support {nearest_support:.2f}"  # Reason for the signal
                return Signal('BUY', current_price, reason, strength)  # Return the BUY signal
                
            # SELL Signal Conditions
            elif (resistance_distance < 0.02  # Price near resistance (2% threshold)
                  and lower_highs  # Confirm downward trend
                  and rsi > 60 and rsi < prev_rsi):  # RSI overbought and falling
                
                # Calculate signal strength factors
                strength_factors = [
                    0.3,  # Base strength
                    0.2 if volume_surge else 0,  # Add strength if volume surges
                    0.3 if rsi > 70 else 0.1,  # Add strength if RSI is very high
                    0.2 * (1 - resistance_distance/0.02)  # Proximity to resistance increases strength
                ]
                
                strength = min(1.0, sum(strength_factors))  # Calculate total strength
                reason = f"Swing Trade SELL: Near resistance {nearest_resistance:.2f}"  # Reason for the signal
                return Signal('SELL', current_price, reason, strength)  # Return the SELL signal
                
            return None  # No signal generated
            
        except Exception as e:
            print(f"Swing strategy error: {e}")  # Log any errors
            return None