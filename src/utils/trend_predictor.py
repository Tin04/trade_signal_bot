from typing import Tuple
import numpy as np
from scipy import stats

class TrendPredictor:
    """
    Predicts potential future trend direction using multiple technical analysis methods.
    Combines different indicators to provide a trend strength and confidence score.
    """

    @staticmethod
    def predict_trend(df) -> Tuple[str, float, str]:
        """
        Analyzes current market data to predict likely trend direction.
        
        Returns:
        - direction: "UP", "DOWN", or "SIDEWAYS"
        - strength: 0-1 score indicating prediction strength
        - reason: Explanation of the prediction
        """
        # Collect various trend signals
        signals = []
        confidences = []
        
        # 1. Moving Average Analysis
        ma_direction, ma_confidence = TrendPredictor._analyze_moving_averages(df)
        signals.append(ma_direction)
        confidences.append(ma_confidence)
        
        # 2. Momentum Analysis
        mom_direction, mom_confidence = TrendPredictor._analyze_momentum(df)
        signals.append(mom_direction)
        confidences.append(mom_confidence)
        
        # 3. Price Pattern Analysis
        pattern_direction, pattern_confidence = TrendPredictor._analyze_price_pattern(df)
        signals.append(pattern_direction)
        confidences.append(pattern_confidence)
        
        # Combine signals and calculate overall direction and strength
        direction, strength, reason = TrendPredictor._combine_signals(signals, confidences)
        
        return direction, strength, reason

    @staticmethod
    def _analyze_moving_averages(df) -> Tuple[str, float]:
        """Analyzes trend using moving averages"""
        try:
            # Compare different timeframe MAs
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            current_price = df['Close'].iloc[-1]
            
            # Calculate trend direction and strength
            if current_price > ma20 > ma50:
                return "UP", min(1.0, (current_price - ma50) / ma50)
            elif current_price < ma20 < ma50:
                return "DOWN", min(1.0, (ma50 - current_price) / current_price)
            else:
                return "SIDEWAYS", 0.3
                
        except Exception as e:
            print(f"MA Analysis error: {e}")
            return "SIDEWAYS", 0.0

    @staticmethod
    def _analyze_momentum(df) -> Tuple[str, float]:
        """Analyzes trend using momentum indicators"""
        try:
            # Use RSI for momentum
            rsi = df['RSI'].iloc[-1]
            
            # Strong momentum signals
            if rsi > 70:
                return "UP", min(1.0, (rsi - 70) / 30)
            elif rsi < 30:
                return "DOWN", min(1.0, (30 - rsi) / 30)
            
            # Check MACD for additional confirmation
            macd = df['MACD'].iloc[-1]
            signal = df['MACD_signal'].iloc[-1]
            
            if macd > signal:
                return "UP", min(1.0, abs(macd - signal))
            elif macd < signal:
                return "DOWN", min(1.0, abs(macd - signal))
            else:
                return "SIDEWAYS", 0.3
                
        except Exception as e:
            print(f"Momentum Analysis error: {e}")
            return "SIDEWAYS", 0.0

    @staticmethod
    def _analyze_price_pattern(df) -> Tuple[str, float]:
        """Analyzes recent price pattern for trend prediction"""
        try:
            # Get recent price data
            recent_prices = df['Close'].tail(10).values
            
            # Calculate linear regression
            x = np.arange(len(recent_prices))
            slope, _, r_value, _, _ = stats.linregress(x, recent_prices)
            
            # Determine trend direction and strength based on slope and R-squared
            r_squared = r_value ** 2
            
            if slope > 0:
                return "UP", min(1.0, r_squared)
            elif slope < 0:
                return "DOWN", min(1.0, r_squared)
            else:
                return "SIDEWAYS", min(1.0, r_squared)
                
        except Exception as e:
            print(f"Pattern Analysis error: {e}")
            return "SIDEWAYS", 0.0

    @staticmethod
    def _combine_signals(signals: list, confidences: list) -> Tuple[str, float, str]:
        """Combines multiple signals into final prediction"""
        if not signals:
            return "SIDEWAYS", 0.0, "Insufficient data"
        
        # Count signal directions
        up_signals = signals.count("UP")
        down_signals = signals.count("DOWN")
        
        # Calculate weighted confidence
        avg_confidence = sum(confidences) / len(confidences)
        
        # Determine overall direction
        if up_signals > down_signals:
            strength = avg_confidence * (up_signals / len(signals))
            reason = f"Bullish signals: {up_signals}/{len(signals)} indicators"
            return "UP", strength, reason
        elif down_signals > up_signals:
            strength = avg_confidence * (down_signals / len(signals))
            reason = f"Bearish signals: {down_signals}/{len(signals)} indicators"
            return "DOWN", strength, reason
        else:
            return "SIDEWAYS", avg_confidence, "Mixed signals" 