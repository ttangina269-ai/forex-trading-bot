# Unit tests for signal generation

import pytest
from src.signals.trend_filter import TrendFilter, TrendFilterResult
from src.signals.confirmation import (
    ConfirmationAnalyzer, Candle, ConfirmationPattern
)


class TestTrendFilter:
    """Test trend filter (1H)."""
    
    def test_trend_filter_initialization(self):
        """Test trend filter initialization."""
        tf = TrendFilter(ema_period=200, threshold_pips=10.0)
        assert tf.ema_period == 200
        assert tf.threshold_pips == 10.0
    
    def test_trend_filter_long_bias(self):
        """Test LONG bias when price > EMA + threshold."""
        tf = TrendFilter(ema_period=200, threshold_pips=10.0, pip_size=0.0001)
        tf.set_ema(1.0900)
        
        # Price is 1.1000, EMA is 1.0900, difference is 100 pips >> 10 pips
        result = tf.analyze(close_price=1.1000)
        
        assert result.bias == "LONG"
        assert result.distance_pips == 100.0
    
    def test_trend_filter_short_bias(self):
        """Test SHORT bias when price < EMA - threshold."""
        tf = TrendFilter(ema_period=200, threshold_pips=10.0, pip_size=0.0001)
        tf.set_ema(1.1000)
        
        # Price is 1.0900, EMA is 1.1000, difference is -100 pips << -10 pips
        result = tf.analyze(close_price=1.0900)
        
        assert result.bias == "SHORT"
        assert result.distance_pips == 100.0
    
    def test_trend_filter_no_trade(self):
        """Test NO_TRADE when price is too close to EMA."""
        tf = TrendFilter(ema_period=200, threshold_pips=10.0, pip_size=0.0001)
        tf.set_ema(1.1000)
        
        # Price is 1.1005, EMA is 1.1000, difference is 5 pips < 10 pips
        result = tf.analyze(close_price=1.1005)
        
        assert result.bias == "NO_TRADE"
        assert result.distance_pips == 5.0
    
    def test_trend_filter_ema_not_set(self):
        """Test error when EMA not set."""
        tf = TrendFilter()
        
        with pytest.raises(ValueError):
            tf.analyze(close_price=1.1000)
    
    def test_trend_filter_invalid_price(self):
        """Test error with invalid price."""
        tf = TrendFilter()
        tf.set_ema(1.0900)
        
        with pytest.raises(ValueError):
            tf.analyze(close_price=-1.1000)  # Negative price
        
        with pytest.raises(ValueError):
            tf.analyze(close_price=None)


class TestConfirmationAnalyzer:
    """Test entry confirmation patterns."""
    
    def test_candle_properties(self):
        """Test candle property calculations."""
        candle = Candle(open_price=1.0, high=1.2, low=0.9, close=1.1)
        
        assert candle.is_bullish() is True
        assert candle.is_bearish() is False
        assert candle.body_size() == 0.1
        assert candle.upper_wick() == 0.1  # 1.2 - 1.1
        assert candle.lower_wick() == 0.1  # 1.0 - 0.9
    
    def test_bullish_engulfing(self):
        """Test bullish engulfing pattern detection."""
        analyzer = ConfirmationAnalyzer()
        
        # Previous: bearish (closes below open)
        prev = Candle(open_price=1.1, high=1.15, low=1.0, close=1.05)
        
        # Current: bullish, larger body, engulfs previous
        curr = Candle(open_price=1.03, high=1.2, low=1.02, close=1.12)
        
        assert analyzer.check_bullish_engulfing(prev, curr) is True
    
    def test_bullish_engulfing_fails_previous_not_bearish(self):
        """Test bullish engulfing fails if previous not bearish."""
        analyzer = ConfirmationAnalyzer()
        
        prev = Candle(open_price=1.0, high=1.15, low=0.9, close=1.1)  # Bullish!
        curr = Candle(open_price=1.08, high=1.2, low=1.0, close=1.12)
        
        assert analyzer.check_bullish_engulfing(prev, curr) is False
    
    def test_bearish_engulfing(self):
        """Test bearish engulfing pattern detection."""
        analyzer = ConfirmationAnalyzer()
        
        # Previous: bullish (closes above open)
        prev = Candle(open_price=1.0, high=1.2, low=0.95, close=1.15)
        
        # Current: bearish, larger body, engulfs previous
        curr = Candle(open_price=1.17, high=1.18, low=0.98, close=1.05)
        
        assert analyzer.check_bearish_engulfing(prev, curr) is True
    
    def test_bullish_rejection(self):
        """Test bullish rejection pattern detection."""
        analyzer = ConfirmationAnalyzer(rejection_wick_ratio=1.5)
        
        # Previous: large lower wick, closes in upper half
        prev = Candle(open_price=1.1, high=1.15, low=1.0, close=1.13)
        # Lower wick = 1.1 - 1.0 = 0.1
        # Body = 1.13 - 1.1 = 0.03
        # Ratio = 0.1 / 0.03 = 3.33 > 1.5 ✓
        # Closes above midpoint: 1.13 > (1.1 + 1.13)/2 ✓
        
        # Current: bullish, closes above previous open
        curr = Candle(open_price=1.12, high=1.16, low=1.11, close=1.14)
        
        assert analyzer.check_bullish_rejection(prev, curr) is True
    
    def test_bearish_rejection(self):
        """Test bearish rejection pattern detection."""
        analyzer = ConfirmationAnalyzer(rejection_wick_ratio=1.5)
        
        # Previous: large upper wick, closes in lower half
        prev = Candle(open_price=1.1, high=1.2, low=1.05, close=1.07)
        # Upper wick = 1.2 - 1.1 = 0.1
        # Body = 1.1 - 1.07 = 0.03
        # Ratio = 0.1 / 0.03 = 3.33 > 1.5 ✓
        # Closes below midpoint: 1.07 < (1.1 + 1.07)/2 ✓
        
        # Current: bearish, closes below previous open
        curr = Candle(open_price=1.08, high=1.09, low=1.04, close=1.06)
        
        assert analyzer.check_bearish_rejection(prev, curr) is True
    
    def test_check_confirmation_long(self):
        """Test confirmation check for LONG direction."""
        analyzer = ConfirmationAnalyzer()
        
        prev = Candle(open_price=1.1, high=1.15, low=1.0, close=1.05)  # Bearish
        curr = Candle(open_price=1.03, high=1.2, low=1.02, close=1.12)  # Bullish engulfing
        
        result = analyzer.check_confirmation(
            prev, curr,
            for_direction="LONG",
            enable_engulfing=True,
            enable_rejection=True
        )
        
        assert result.pattern_found is True
        assert result.pattern_type == "BULLISH_ENGULFING"
        assert result.direction == "LONG"
    
    def test_check_confirmation_short(self):
        """Test confirmation check for SHORT direction."""
        analyzer = ConfirmationAnalyzer()
        
        prev = Candle(open_price=1.0, high=1.2, low=0.95, close=1.15)  # Bullish
        curr = Candle(open_price=1.17, high=1.18, low=0.98, close=1.05)  # Bearish engulfing
        
        result = analyzer.check_confirmation(
            prev, curr,
            for_direction="SHORT",
            enable_engulfing=True,
            enable_rejection=True
        )
        
        assert result.pattern_found is True
        assert result.pattern_type == "BEARISH_ENGULFING"
        assert result.direction == "SHORT"
    
    def test_check_confirmation_disabled_patterns(self):
        """Test confirmation returns False when patterns disabled."""
        analyzer = ConfirmationAnalyzer()
        
        prev = Candle(open_price=1.1, high=1.15, low=1.0, close=1.05)
        curr = Candle(open_price=1.03, high=1.2, low=1.02, close=1.12)
        
        # Disable both patterns
        result = analyzer.check_confirmation(
            prev, curr,
            for_direction="LONG",
            enable_engulfing=False,
            enable_rejection=False
        )
        
        assert result.pattern_found is False
