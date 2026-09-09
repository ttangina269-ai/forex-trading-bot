# Entry Confirmation Patterns

from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Candle:
    """OHLC candle data."""
    open_price: float
    high: float
    low: float
    close: float
    
    def body_size(self) -> float:
        """Size of candle body (absolute)."""
        return abs(self.close - self.open_price)
    
    def is_bullish(self) -> bool:
        """True if close > open."""
        return self.close > self.open_price
    
    def is_bearish(self) -> bool:
        """True if close < open."""
        return self.close < self.open_price
    
    def upper_wick(self) -> float:
        """Upper wick (shadow) size."""
        return self.high - max(self.open_price, self.close)
    
    def lower_wick(self) -> float:
        """Lower wick (shadow) size."""
        return min(self.open_price, self.close) - self.low


@dataclass
class ConfirmationPattern:
    """Result of entry confirmation check."""
    pattern_found: bool
    pattern_type: Optional[str]  # "BULLISH_ENGULFING", "BEARISH_ENGULFING", etc.
    direction: Optional[str]  # "LONG" or "SHORT"
    
    def __str__(self) -> str:
        if self.pattern_found:
            return f"Confirmation: {self.pattern_type} ({self.direction})"
        return "No confirmation pattern found"


class ConfirmationAnalyzer:
    """
    Analyzes price-action confirmation patterns for entry.
    
    Patterns checked:
    - Bullish engulfing (2 candles)
    - Bearish engulfing (2 candles)
    - Bullish rejection (2 candles)
    - Bearish rejection (2 candles)
    """
    
    def __init__(self, rejection_wick_ratio: float = 1.5):
        """
        Args:
            rejection_wick_ratio: Minimum wick/body ratio for rejection pattern
        """
        if rejection_wick_ratio < 1.0:
            raise ValueError("Rejection wick ratio must be >= 1.0")
        
        self.rejection_wick_ratio = rejection_wick_ratio
    
    def check_bullish_engulfing(self, prev_candle: Candle, 
                                curr_candle: Candle) -> bool:
        """
        Check for bullish engulfing pattern.
        
        Requirements:
        1. Previous candle is bearish
        2. Current candle is bullish
        3. Current opens <= previous open
        4. Current closes > previous close
        5. Current body >= previous body
        
        Args:
            prev_candle: Previous candle
            curr_candle: Current candle
            
        Returns:
            True if bullish engulfing found
        """
        # Previous must be bearish
        if not prev_candle.is_bearish():
            return False
        
        # Current must be bullish
        if not curr_candle.is_bullish():
            return False
        
        # Current opens at or below previous open
        if curr_candle.open_price > prev_candle.open_price:
            return False
        
        # Current closes above previous close
        if curr_candle.close <= prev_candle.close:
            return False
        
        # Current body is >= previous body
        if curr_candle.body_size() < prev_candle.body_size():
            return False
        
        logger.debug(
            f"Bullish Engulfing: "
            f"Prev(O:{prev_candle.open_price}, C:{prev_candle.close}) -> "
            f"Curr(O:{curr_candle.open_price}, C:{curr_candle.close})"
        )
        
        return True
    
    def check_bearish_engulfing(self, prev_candle: Candle, 
                                curr_candle: Candle) -> bool:
        """
        Check for bearish engulfing pattern.
        
        Requirements:
        1. Previous candle is bullish
        2. Current candle is bearish
        3. Current opens >= previous open
        4. Current closes < previous close
        5. Current body >= previous body
        
        Args:
            prev_candle: Previous candle
            curr_candle: Current candle
            
        Returns:
            True if bearish engulfing found
        """
        # Previous must be bullish
        if not prev_candle.is_bullish():
            return False
        
        # Current must be bearish
        if not curr_candle.is_bearish():
            return False
        
        # Current opens at or above previous open
        if curr_candle.open_price < prev_candle.open_price:
            return False
        
        # Current closes below previous close
        if curr_candle.close >= prev_candle.close:
            return False
        
        # Current body is >= previous body
        if curr_candle.body_size() < prev_candle.body_size():
            return False
        
        logger.debug(
            f"Bearish Engulfing: "
            f"Prev(O:{prev_candle.open_price}, C:{prev_candle.close}) -> "
            f"Curr(O:{curr_candle.open_price}, C:{curr_candle.close})"
        )
        
        return True
    
    def check_bullish_rejection(self, prev_candle: Candle, 
                               curr_candle: Candle) -> bool:
        """
        Check for bullish rejection pattern.
        
        Requirements:
        1. Previous candle has large lower wick
        2. Previous candle closes in upper half
        3. Current candle is bullish
        4. Current closes above previous open
        
        Args:
            prev_candle: Previous candle
            curr_candle: Current candle
            
        Returns:
            True if bullish rejection found
        """
        # Calculate lower wick
        lower_wick = prev_candle.lower_wick()
        body = prev_candle.body_size()
        
        # Avoid division by zero
        if body < 0.00001:  # Very small body
            # For small body, accept good wick ratio
            if lower_wick < 0.0001:
                return False
        else:
            wick_ratio = lower_wick / body
            if wick_ratio < self.rejection_wick_ratio:
                return False
        
        # Previous closes in upper half
        midpoint = (prev_candle.open_price + prev_candle.close) / 2
        if prev_candle.close <= midpoint:
            return False
        
        # Current is bullish
        if not curr_candle.is_bullish():
            return False
        
        # Current closes above previous open
        if curr_candle.close <= prev_candle.open_price:
            return False
        
        logger.debug(
            f"Bullish Rejection: Lower wick {lower_wick:.5f}, "
            f"ratio {lower_wick/max(body, 0.0001):.2f}"
        )
        
        return True
    
    def check_bearish_rejection(self, prev_candle: Candle, 
                               curr_candle: Candle) -> bool:
        """
        Check for bearish rejection pattern.
        
        Requirements:
        1. Previous candle has large upper wick
        2. Previous candle closes in lower half
        3. Current candle is bearish
        4. Current closes below previous open
        
        Args:
            prev_candle: Previous candle
            curr_candle: Current candle
            
        Returns:
            True if bearish rejection found
        """
        # Calculate upper wick
        upper_wick = prev_candle.upper_wick()
        body = prev_candle.body_size()
        
        # Avoid division by zero
        if body < 0.00001:  # Very small body
            if upper_wick < 0.0001:
                return False
        else:
            wick_ratio = upper_wick / body
            if wick_ratio < self.rejection_wick_ratio:
                return False
        
        # Previous closes in lower half
        midpoint = (prev_candle.open_price + prev_candle.close) / 2
        if prev_candle.close >= midpoint:
            return False
        
        # Current is bearish
        if not curr_candle.is_bearish():
            return False
        
        # Current closes below previous open
        if curr_candle.close >= prev_candle.open_price:
            return False
        
        logger.debug(
            f"Bearish Rejection: Upper wick {upper_wick:.5f}, "
            f"ratio {upper_wick/max(body, 0.0001):.2f}"
        )
        
        return True
    
    def check_confirmation(
        self,
        prev_candle: Candle,
        curr_candle: Candle,
        for_direction: str,
        enable_engulfing: bool = True,
        enable_rejection: bool = True
    ) -> ConfirmationPattern:
        """
        Check if confirmation pattern exists for a given direction.
        
        Args:
            prev_candle: Previous 15M candle
            curr_candle: Current 15M candle
            for_direction: "LONG" or "SHORT"
            enable_engulfing: Check engulfing patterns
            enable_rejection: Check rejection patterns
            
        Returns:
            ConfirmationPattern result
        """
        if for_direction not in ["LONG", "SHORT"]:
            raise ValueError(f"Invalid direction: {for_direction}")
        
        if for_direction == "LONG":
            if enable_engulfing and self.check_bullish_engulfing(prev_candle, curr_candle):
                return ConfirmationPattern(
                    pattern_found=True,
                    pattern_type="BULLISH_ENGULFING",
                    direction="LONG"
                )
            
            if enable_rejection and self.check_bullish_rejection(prev_candle, curr_candle):
                return ConfirmationPattern(
                    pattern_found=True,
                    pattern_type="BULLISH_REJECTION",
                    direction="LONG"
                )
        
        else:  # SHORT
            if enable_engulfing and self.check_bearish_engulfing(prev_candle, curr_candle):
                return ConfirmationPattern(
                    pattern_found=True,
                    pattern_type="BEARISH_ENGULFING",
                    direction="SHORT"
                )
            
            if enable_rejection and self.check_bearish_rejection(prev_candle, curr_candle):
                return ConfirmationPattern(
                    pattern_found=True,
                    pattern_type="BEARISH_REJECTION",
                    direction="SHORT"
                )
        
        return ConfirmationPattern(
            pattern_found=False,
            pattern_type=None,
            direction=None
        )
