# Signal Generation - Trend Filter

from typing import Optional, Literal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrendFilterResult:
    """Result of trend filter analysis."""
    bias: Literal["LONG", "SHORT", "NO_TRADE"]
    close_price: float
    ema_200: float
    distance_from_ema: float  # Positive = price above EMA
    distance_pips: float
    threshold_pips: float
    
    def __str__(self) -> str:
        return (
            f"Bias: {self.bias} | "
            f"Close: {self.close_price:.5f} | "
            f"200 EMA: {self.ema_200:.5f} | "
            f"Distance: {self.distance_pips:.1f} pips "
            f"(threshold: {self.threshold_pips:.1f})"
        )


class TrendFilter:
    """
    1H timeframe trend filter using 200 EMA.
    
    Determines whether to trade LONG, SHORT, or not at all.
    Price must be sufficiently away from 200 EMA to indicate clear trend.
    """
    
    def __init__(self, ema_period: int = 200, 
                 threshold_pips: float = 10.0,
                 pip_size: float = 0.0001):
        """
        Args:
            ema_period: Period for trend EMA (default 200)
            threshold_pips: Minimum distance from EMA to trade (default 10 pips)
            pip_size: Pip value for the currency pair (default 0.0001)
        """
        self.ema_period = ema_period
        self.threshold_pips = threshold_pips
        self.pip_size = pip_size
        self.threshold_price = threshold_pips * pip_size
        self.ema_200: Optional[float] = None
    
    def set_ema(self, ema_value: float):
        """
        Set the current 200 EMA value from indicator.
        
        Args:
            ema_value: Current 200 EMA value
        """
        if ema_value is None or ema_value <= 0:
            raise ValueError(f"Invalid EMA value: {ema_value}")
        
        self.ema_200 = ema_value
    
    def analyze(self, close_price: float) -> TrendFilterResult:
        """
        Analyze current price against 200 EMA to determine trend.
        
        Args:
            close_price: Most recent 1H close price
            
        Returns:
            TrendFilterResult with bias and analysis details
            
        Raises:
            ValueError: If EMA not set or invalid price
        """
        if self.ema_200 is None:
            raise ValueError("200 EMA not set. Call set_ema() first.")
        
        if close_price is None or close_price <= 0:
            raise ValueError(f"Invalid close price: {close_price}")
        
        # Calculate distance from EMA
        distance_from_ema = close_price - self.ema_200
        distance_pips = abs(distance_from_ema) / self.pip_size
        
        # Determine bias
        if distance_from_ema > self.threshold_price:
            # Price is above EMA by more than threshold
            bias = "LONG"
        elif distance_from_ema < -self.threshold_price:
            # Price is below EMA by more than threshold
            bias = "SHORT"
        else:
            # Price is too close to EMA (indecision zone)
            bias = "NO_TRADE"
        
        result = TrendFilterResult(
            bias=bias,
            close_price=close_price,
            ema_200=self.ema_200,
            distance_from_ema=distance_from_ema,
            distance_pips=distance_pips,
            threshold_pips=self.threshold_pips
        )
        
        logger.debug(f"Trend Filter: {result}")
        
        return result
