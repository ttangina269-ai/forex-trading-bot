# Core Indicator Calculations

from typing import List, Optional
import numpy as np


class EMA:
    """
    Exponential Moving Average indicator.
    
    The EMA gives more weight to recent prices.
    Formula: EMA = (Price × Multiplier) + (EMA_Previous × (1 - Multiplier))
    Multiplier = 2 / (Period + 1)
    """
    
    def __init__(self, period: int):
        """
        Args:
            period: Number of periods for EMA calculation
        """
        if period < 1:
            raise ValueError("Period must be >= 1")
        
        self.period = period
        self.multiplier = 2.0 / (period + 1)
        self.ema_value: Optional[float] = None
        self.price_history: List[float] = []
    
    def add_price(self, price: float) -> Optional[float]:
        """
        Add a new price and calculate updated EMA.
        
        Args:
            price: New closing price
            
        Returns:
            The updated EMA value, or None if not enough data yet
        """
        if price is None or price < 0:
            raise ValueError(f"Invalid price: {price}")
        
        self.price_history.append(price)
        
        # Need minimum period candles to calculate initial EMA
        if len(self.price_history) < self.period:
            return None
        
        # First EMA = Simple Moving Average
        if self.ema_value is None:
            self.ema_value = np.mean(self.price_history[:self.period])
            return self.ema_value
        
        # Subsequent EMAs use exponential smoothing
        self.ema_value = (price * self.multiplier) + \
                        (self.ema_value * (1 - self.multiplier))
        
        return self.ema_value
    
    def get_ema(self) -> Optional[float]:
        """
        Get the current EMA value.
        
        Returns:
            Current EMA or None if not enough data
        """
        return self.ema_value
    
    def reset(self):
        """
        Reset the indicator for a new calculation.
        """
        self.ema_value = None
        self.price_history = []


class ATR:
    """
    Average True Range indicator.
    
    Measures market volatility. True Range is the greatest of:
    1. High - Low
    2. |High - Previous Close|
    3. |Low - Previous Close|
    
    ATR is the EMA of True Range.
    """
    
    def __init__(self, period: int = 14):
        """
        Args:
            period: Number of periods for ATR calculation (default 14)
        """
        if period < 1:
            raise ValueError("Period must be >= 1")
        
        self.period = period
        self.multiplier = 1.0 / period  # Simple average for first value
        self.atr_value: Optional[float] = None
        self.true_ranges: List[float] = []
        self.previous_close: Optional[float] = None
    
    def calculate_true_range(self, high: float, low: float, 
                            previous_close: Optional[float]) -> float:
        """
        Calculate True Range for a candle.
        
        Args:
            high: Candle high price
            low: Candle low price
            previous_close: Previous candle close price
            
        Returns:
            True Range value
        """
        if high < low:
            raise ValueError(f"Invalid prices: high {high} < low {low}")
        
        tr1 = high - low
        
        if previous_close is None:
            return tr1
        
        tr2 = abs(high - previous_close)
        tr3 = abs(low - previous_close)
        
        return max(tr1, tr2, tr3)
    
    def add_candle(self, high: float, low: float, close: float) -> Optional[float]:
        """
        Add a new candle and calculate updated ATR.
        
        Args:
            high: Candle high price
            low: Candle low price
            close: Candle close price
            
        Returns:
            Updated ATR value, or None if not enough data yet
        """
        if high is None or low is None or close is None:
            raise ValueError("Price data cannot be None")
        
        if high < low or high < close or low > close:
            raise ValueError(f"Invalid OHLC: H={high}, L={low}, C={close}")
        
        # Calculate true range
        tr = self.calculate_true_range(high, low, self.previous_close)
        self.true_ranges.append(tr)
        self.previous_close = close
        
        # Need minimum period TR values
        if len(self.true_ranges) < self.period:
            return None
        
        # First ATR = Simple average of True Ranges
        if self.atr_value is None:
            self.atr_value = np.mean(self.true_ranges[:self.period])
            return self.atr_value
        
        # Subsequent ATRs use smoothed average
        self.atr_value = (tr * self.multiplier) + \
                        (self.atr_value * (1 - self.multiplier))
        
        return self.atr_value
    
    def get_atr(self) -> Optional[float]:
        """
        Get the current ATR value.
        
        Returns:
            Current ATR or None if not enough data
        """
        return self.atr_value
    
    def reset(self):
        """
        Reset the indicator for new calculation.
        """
        self.atr_value = None
        self.true_ranges = []
        self.previous_close = None


class SwingDetector:
    """
    Detects swing highs and lows for stop loss placement.
    
    A swing high is a candle with highs lower on both sides.
    A swing low is a candle with lows higher on both sides.
    """
    
    def __init__(self, lookback: int = 5):
        """
        Args:
            lookback: Number of candles on each side to check
        """
        if lookback < 1:
            raise ValueError("Lookback must be >= 1")
        
        self.lookback = lookback
        self.candles: List[dict] = []
    
    def add_candle(self, high: float, low: float, close: float):
        """
        Add a new candle to the history.
        
        Args:
            high: Candle high
            low: Candle low
            close: Candle close
        """
        self.candles.append({
            'high': high,
            'low': low,
            'close': close
        })
    
    def get_swing_high(self) -> Optional[float]:
        """
        Get the most recent swing high.
        
        A swing high requires at least lookback candles after it.
        
        Returns:
            The swing high price, or None if not enough data
        """
        required_candles = self.lookback * 2 + 1
        
        if len(self.candles) < required_candles:
            return None
        
        # Look at the middle candle (offset from end)
        middle_idx = len(self.candles) - self.lookback - 1
        middle_high = self.candles[middle_idx]['high']
        
        # Check if all candles before are lower
        for i in range(middle_idx - self.lookback, middle_idx):
            if self.candles[i]['high'] > middle_high:
                return None
        
        # Check if all candles after are lower
        for i in range(middle_idx + 1, middle_idx + self.lookback + 1):
            if self.candles[i]['high'] > middle_high:
                return None
        
        return middle_high
    
    def get_swing_low(self) -> Optional[float]:
        """
        Get the most recent swing low.
        
        A swing low requires at least lookback candles after it.
        
        Returns:
            The swing low price, or None if not enough data
        """
        required_candles = self.lookback * 2 + 1
        
        if len(self.candles) < required_candles:
            return None
        
        # Look at the middle candle (offset from end)
        middle_idx = len(self.candles) - self.lookback - 1
        middle_low = self.candles[middle_idx]['low']
        
        # Check if all candles before are higher
        for i in range(middle_idx - self.lookback, middle_idx):
            if self.candles[i]['low'] < middle_low:
                return None
        
        # Check if all candles after are higher
        for i in range(middle_idx + 1, middle_idx + self.lookback + 1):
            if self.candles[i]['low'] < middle_low:
                return None
        
        return middle_low
    
    def reset(self):
        """
        Reset the indicator.
        """
        self.candles = []
