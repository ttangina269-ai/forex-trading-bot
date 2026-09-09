# Risk Validation - Filter trades based on multiple criteria

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskValidationResult:
    """Result of risk validation check."""
    valid: bool
    reason: Optional[str] = None  # Reason if invalid
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    def __str__(self) -> str:
        if self.valid:
            msg = "VALID"
            if self.warnings:
                msg += f" (Warnings: {'; '.join(self.warnings)})"
            return msg
        return f"INVALID: {self.reason}"


class RiskValidator:
    """
    Validates trades against multiple risk and filter criteria.
    
    Checks:
    - Spread constraints
    - Volatility (ATR) constraints
    - Trading session filters
    - Day-of-week filters
    - Daily/weekly/monthly loss limits
    - Maximum drawdown
    - Consecutive loss limits
    - Position count limits
    """
    
    def __init__(self):
        """Initialize validator."""
        pass
    
    def validate_spread(self, current_spread: float, 
                       max_spread: float) -> RiskValidationResult:
        """
        Check if current spread is acceptable.
        
        Args:
            current_spread: Current bid-ask spread in pips
            max_spread: Maximum allowed spread in pips
            
        Returns:
            RiskValidationResult
        """
        if current_spread is None or current_spread < 0:
            return RiskValidationResult(
                valid=False,
                reason=f"Invalid spread: {current_spread}"
            )
        
        if current_spread > max_spread:
            return RiskValidationResult(
                valid=False,
                reason=f"Spread {current_spread:.1f} pips > max {max_spread:.1f} pips"
            )
        
        if current_spread > max_spread * 0.75:  # Warning if >75% of max
            return RiskValidationResult(
                valid=True,
                warnings=[f"Spread {current_spread:.1f} is high ({(current_spread/max_spread*100):.0f}% of max)"]
            )
        
        logger.debug(f"Spread check passed: {current_spread:.1f} <= {max_spread:.1f}")
        
        return RiskValidationResult(valid=True)
    
    def validate_volatility(self, atr_value: float,
                           min_atr: float = 0.0,
                           max_atr: float = 0.0) -> RiskValidationResult:
        """
        Check if current volatility is in acceptable range.
        
        Args:
            atr_value: Current ATR in pips
            min_atr: Minimum ATR threshold (0 = disabled)
            max_atr: Maximum ATR threshold (0 = disabled)
            
        Returns:
            RiskValidationResult
        """
        if atr_value is None or atr_value < 0:
            return RiskValidationResult(
                valid=False,
                reason=f"Invalid ATR: {atr_value}"
            )
        
        if min_atr > 0 and atr_value < min_atr:
            return RiskValidationResult(
                valid=False,
                reason=f"ATR {atr_value:.1f} < minimum {min_atr:.1f}"
            )
        
        if max_atr > 0 and atr_value > max_atr:
            return RiskValidationResult(
                valid=False,
                reason=f"ATR {atr_value:.1f} > maximum {max_atr:.1f}"
            )
        
        logger.debug(f"Volatility check passed: {atr_value:.1f} pips")
        
        return RiskValidationResult(valid=True)
    
    def validate_session(self, current_utc_time: datetime,
                        allowed_sessions: List[str]) -> RiskValidationResult:
        """
        Check if current time is within allowed trading sessions.
        
        Sessions (UTC):
        - london: 08:00-17:00
        - newyork: 13:00-22:00
        - tokyo: 21:00-06:00 (next day)
        - sydney: 22:00-07:00 (next day)
        
        Args:
            current_utc_time: Current UTC time
            allowed_sessions: List of allowed session names
            
        Returns:
            RiskValidationResult
        """
        if not allowed_sessions or "all" in [s.lower() for s in allowed_sessions]:
            logger.debug("Session filter: All sessions allowed")
            return RiskValidationResult(valid=True)
        
        hour = current_utc_time.hour
        active_sessions = []
        
        for session in allowed_sessions:
            session = session.lower()
            
            if session == "london" and 8 <= hour < 17:
                active_sessions.append("london")
            elif session == "newyork" and 13 <= hour < 22:
                active_sessions.append("newyork")
            elif session == "tokyo" and (21 <= hour or hour < 6):
                active_sessions.append("tokyo")
            elif session == "sydney" and (22 <= hour or hour < 7):
                active_sessions.append("sydney")
        
        if active_sessions:
            logger.debug(f"Active sessions: {active_sessions}")
            return RiskValidationResult(valid=True)
        
        return RiskValidationResult(
            valid=False,
            reason=f"Current time {hour:02d}:00 UTC outside allowed sessions {allowed_sessions}"
        )
    
    def validate_day_of_week(self, current_utc_time: datetime,
                            allowed_days: List[str]) -> RiskValidationResult:
        """
        Check if current day is allowed for trading.
        
        Args:
            current_utc_time: Current UTC time
            allowed_days: List of allowed day names (monday-friday)
            
        Returns:
            RiskValidationResult
        """
        day_name = current_utc_time.strftime('%A').lower()
        
        if day_name not in [d.lower() for d in allowed_days]:
            return RiskValidationResult(
                valid=False,
                reason=f"Trading not allowed on {day_name} (allowed: {allowed_days})"
            )
        
        logger.debug(f"Day of week check passed: {day_name}")
        
        return RiskValidationResult(valid=True)
    
    def validate_daily_loss_limit(self, daily_loss: float,
                                 account_equity: float,
                                 max_daily_loss_pct: float) -> RiskValidationResult:
        """
        Check if daily loss limit exceeded.
        
        Args:
            daily_loss: Total loss for the day (positive number)
            account_equity: Current account equity
            max_daily_loss_pct: Maximum daily loss as % of equity
            
        Returns:
            RiskValidationResult
        """
        max_loss_amount = account_equity * max_daily_loss_pct
        
        if daily_loss >= max_loss_amount:
            return RiskValidationResult(
                valid=False,
                reason=f"Daily loss ${daily_loss:.2f} >= limit ${max_loss_amount:.2f} ({max_daily_loss_pct*100:.1f}%)"
            )
        
        # Warning if close to limit
        if daily_loss > max_loss_amount * 0.75:
            pct_remaining = ((max_loss_amount - daily_loss) / max_loss_amount) * 100
            return RiskValidationResult(
                valid=True,
                warnings=[f"Daily loss limit {pct_remaining:.0f}% remaining"]
            )
        
        logger.debug(f"Daily loss check passed: ${daily_loss:.2f} < ${max_loss_amount:.2f}")
        
        return RiskValidationResult(valid=True)
    
    def validate_drawdown(self, current_equity: float,
                         peak_equity: float,
                         max_drawdown_pct: float) -> RiskValidationResult:
        """
        Check if maximum drawdown exceeded.
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity since start
            max_drawdown_pct: Maximum drawdown as % of peak
            
        Returns:
            RiskValidationResult
        """
        if peak_equity <= 0:
            return RiskValidationResult(
                valid=False,
                reason="Invalid peak equity"
            )
        
        drawdown = (peak_equity - current_equity) / peak_equity
        
        if drawdown >= max_drawdown_pct:
            return RiskValidationResult(
                valid=False,
                reason=f"Drawdown {drawdown*100:.2f}% >= limit {max_drawdown_pct*100:.2f}%"
            )
        
        # Warning if close to limit
        if drawdown > max_drawdown_pct * 0.75:
            remaining_pct = ((max_drawdown_pct - drawdown) / max_drawdown_pct) * 100
            return RiskValidationResult(
                valid=True,
                warnings=[f"Drawdown limit {remaining_pct:.0f}% remaining"]
            )
        
        logger.debug(f"Drawdown check passed: {drawdown*100:.2f}% <= {max_drawdown_pct*100:.2f}%")
        
        return RiskValidationResult(valid=True)
    
    def validate_consecutive_losses(self, consecutive_losses: int,
                                   max_consecutive: int) -> RiskValidationResult:
        """
        Check if consecutive loss limit exceeded.
        
        Args:
            consecutive_losses: Current number of consecutive losses
            max_consecutive: Maximum allowed consecutive losses
            
        Returns:
            RiskValidationResult
        """
        if consecutive_losses >= max_consecutive:
            return RiskValidationResult(
                valid=False,
                reason=f"Consecutive losses {consecutive_losses} >= limit {max_consecutive}"
            )
        
        # Warning if approaching limit
        if consecutive_losses >= max_consecutive * 0.7:
            return RiskValidationResult(
                valid=True,
                warnings=[f"Approaching consecutive loss limit ({consecutive_losses}/{max_consecutive})"]
            )
        
        logger.debug(f"Consecutive loss check passed: {consecutive_losses} < {max_consecutive}")
        
        return RiskValidationResult(valid=True)
    
    def validate_position_count(self, open_positions: int,
                               max_positions: int) -> RiskValidationResult:
        """
        Check if maximum position count exceeded.
        
        Args:
            open_positions: Number of currently open positions
            max_positions: Maximum allowed open positions
            
        Returns:
            RiskValidationResult
        """
        if open_positions >= max_positions:
            return RiskValidationResult(
                valid=False,
                reason=f"Open positions {open_positions} >= limit {max_positions}"
            )
        
        logger.debug(f"Position count check passed: {open_positions} < {max_positions}")
        
        return RiskValidationResult(valid=True)
