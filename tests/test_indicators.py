# Unit tests for indicator calculations

import pytest
from src.indicators.ema import EMA, ATR, SwingDetector


class TestEMA:
    """Test EMA indicator."""
    
    def test_ema_initialization(self):
        """Test EMA initialization."""
        ema = EMA(20)
        assert ema.period == 20
        assert ema.ema_value is None
        assert ema.get_ema() is None
    
    def test_ema_invalid_period(self):
        """Test invalid period raises error."""
        with pytest.raises(ValueError):
            EMA(0)
        with pytest.raises(ValueError):
            EMA(-5)
    
    def test_ema_calculation(self):
        """Test EMA calculation with known values."""
        ema = EMA(3)
        
        # Add prices: 1, 2, 3, 4, 5
        prices = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        for i, price in enumerate(prices):
            result = ema.add_price(price)
            
            if i < 2:  # First 2 prices
                assert result is None
            else:
                assert result is not None
                assert result > 0
    
    def test_ema_reset(self):
        """Test EMA reset."""
        ema = EMA(5)
        ema.add_price(1.0)
        ema.add_price(2.0)
        ema.add_price(3.0)
        
        assert ema.get_ema() is not None
        
        ema.reset()
        assert ema.get_ema() is None
        assert len(ema.price_history) == 0


class TestATR:
    """Test ATR indicator."""
    
    def test_atr_initialization(self):
        """Test ATR initialization."""
        atr = ATR(14)
        assert atr.period == 14
        assert atr.get_atr() is None
    
    def test_true_range_calculation(self):
        """Test individual true range calculations."""
        atr = ATR(14)
        
        # Test 1: High - Low is largest
        tr = atr.calculate_true_range(high=1.5, low=1.0, previous_close=None)
        assert tr == 0.5
        
        # Test 2: With previous close
        tr = atr.calculate_true_range(high=1.6, low=1.0, previous_close=1.4)
        expected = max(0.6, abs(1.6 - 1.4), abs(1.0 - 1.4))
        assert tr == expected
    
    def test_atr_invalid_prices(self):
        """Test invalid prices raise error."""
        atr = ATR(14)
        
        with pytest.raises(ValueError):
            atr.add_candle(high=1.0, low=1.5, close=1.2)  # high < low
    
    def test_atr_calculation_series(self):
        """Test ATR calculation with candle series."""
        atr = ATR(3)
        
        candles = [
            {"high": 1.5, "low": 1.0, "close": 1.2},
            {"high": 1.6, "low": 1.1, "close": 1.3},
            {"high": 1.7, "low": 1.2, "close": 1.5},
            {"high": 1.8, "low": 1.3, "close": 1.6},
        ]
        
        for i, candle in enumerate(candles):
            result = atr.add_candle(
                high=candle["high"],
                low=candle["low"],
                close=candle["close"]
            )
            
            if i < 2:  # First 2 candles
                assert result is None
            else:
                assert result is not None
                assert result > 0


class TestSwingDetector:
    """Test swing high/low detection."""
    
    def test_swing_initialization(self):
        """Test swing detector initialization."""
        detector = SwingDetector(lookback=5)
        assert detector.lookback == 5
        assert len(detector.candles) == 0
    
    def test_swing_invalid_lookback(self):
        """Test invalid lookback raises error."""
        with pytest.raises(ValueError):
            SwingDetector(lookback=0)
    
    def test_swing_high_detection(self):
        """Test swing high detection."""
        detector = SwingDetector(lookback=2)
        
        # Pattern: low, high, low (middle is swing high)
        detector.add_candle(high=1.4, low=1.0, close=1.2)
        detector.add_candle(high=1.8, low=1.2, close=1.7)  # Should be swing high
        detector.add_candle(high=1.6, low=1.1, close=1.3)
        detector.add_candle(high=1.7, low=1.2, close=1.5)
        detector.add_candle(high=1.6, low=1.0, close=1.3)
        
        swing_high = detector.get_swing_high()
        assert swing_high is not None
        assert swing_high == 1.8
    
    def test_swing_low_detection(self):
        """Test swing low detection."""
        detector = SwingDetector(lookback=2)
        
        # Pattern: high, low, high (middle is swing low)
        detector.add_candle(high=1.8, low=1.4, close=1.6)
        detector.add_candle(high=1.6, low=1.0, close=1.2)  # Should be swing low
        detector.add_candle(high=1.9, low=1.3, close=1.7)
        detector.add_candle(high=1.8, low=1.2, close=1.5)
        detector.add_candle(high=1.9, low=1.3, close=1.7)
        
        swing_low = detector.get_swing_low()
        assert swing_low is not None
        assert swing_low == 1.0
    
    def test_swing_not_enough_data(self):
        """Test swing detection with insufficient data."""
        detector = SwingDetector(lookback=5)
        
        # Only add 3 candles (need 11 for lookback=5)
        detector.add_candle(high=1.5, low=1.0, close=1.2)
        detector.add_candle(high=1.6, low=1.1, close=1.3)
        detector.add_candle(high=1.7, low=1.2, close=1.5)
        
        assert detector.get_swing_high() is None
        assert detector.get_swing_low() is None
