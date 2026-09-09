# Trade Logging - Comprehensive logging for all trade decisions

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json


class TradeLogger:
    """
    Specialized logger for trade decisions and execution.
    
    Logs every trade entry, exit, rejection, and risk management event.
    """
    
    def __init__(self, log_file: str = "logs/trading.log"):
        """
        Initialize trade logger.
        
        Args:
            log_file: Path to log file
        """
        self.logger = logging.getLogger("trade_logger")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_entry(self, symbol: str, direction: str, details: Dict[str, Any]):
        """
        Log a trade entry.
        
        Args:
            symbol: Currency pair
            direction: LONG or SHORT
            details: Dictionary with entry details
                - entry_price
                - stop_loss
                - take_profit
                - position_size
                - risk_amount
                - spread
                - 1h_trend
                - 200_ema
                - pullback_status
                - confirmation_pattern
                - reason
        """
        msg = (
            f"[ENTRY] {symbol} {direction}\n"
            f"  Entry Price: {details.get('entry_price', 'N/A')}\n"
            f"  Stop Loss: {details.get('stop_loss', 'N/A')} "
            f"({details.get('sl_pips', 0):.1f} pips)\n"
            f"  Take Profit: {details.get('take_profit', 'N/A')} "
            f"({details.get('tp_pips', 0):.1f} pips)\n"
            f"  Position Size: {details.get('position_size', 'N/A')} lots\n"
            f"  Risk Amount: ${details.get('risk_amount', 'N/A')}\n"
            f"  Risk %: {details.get('risk_pct', 'N/A')}%\n"
            f"  Spread: {details.get('spread', 'N/A')} pips\n"
            f"  1H Trend: {details.get('1h_trend', 'N/A')} "
            f"(200 EMA: {details.get('200_ema', 'N/A')})\n"
            f"  Pullback: {details.get('pullback_status', 'N/A')}\n"
            f"  Confirmation: {details.get('confirmation_pattern', 'N/A')}\n"
            f"  Reason: {details.get('reason', 'N/A')}"
        )
        self.logger.info(msg)
    
    def log_rejection(self, symbol: str, reason: str, details: Dict[str, Any] = None):
        """
        Log a rejected trade setup.
        
        Args:
            symbol: Currency pair
            reason: Reason for rejection
            details: Optional additional context
        """
        msg = f"[REJECTED] {symbol} - {reason}"
        
        if details:
            msg += f"\n  Context: {json.dumps(details, default=str)}"
        
        self.logger.warning(msg)
    
    def log_exit(self, symbol: str, direction: str, details: Dict[str, Any]):
        """
        Log a trade exit.
        
        Args:
            symbol: Currency pair
            direction: LONG or SHORT
            details: Dictionary with exit details
                - entry_price
                - exit_price
                - exit_reason (TP, SL, MANUAL)
                - pnl
                - pnl_pct
                - r_value
                - duration
        """
        exit_reason = details.get('exit_reason', 'UNKNOWN')
        pnl = details.get('pnl', 0)
        pnl_pct = details.get('pnl_pct', 0)
        r_value = details.get('r_value', 0)
        
        # Color coding for visual clarity
        pnl_sign = '+' if pnl >= 0 else ''
        r_sign = '+' if r_value >= 0 else ''
        
        msg = (
            f"[EXIT] {symbol} {direction} - {exit_reason}\n"
            f"  Entry: {details.get('entry_price', 'N/A')} @ {details.get('entry_time', 'N/A')}\n"
            f"  Exit: {details.get('exit_price', 'N/A')} @ {details.get('exit_time', 'N/A')}\n"
            f"  P&L: {pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.2f}%)\n"
            f"  R Value: {r_sign}{r_value:.2f}R\n"
            f"  Duration: {details.get('duration', 'N/A')}"
        )
        self.logger.info(msg)
    
    def log_risk_limit(self, limit_type: str, current: float, limit: float):
        """
        Log when a risk limit is triggered.
        
        Args:
            limit_type: Type of limit (daily_loss, drawdown, consecutive_losses)
            current: Current value
            limit: Limit value
        """
        msg = f"[LIMIT TRIGGERED] {limit_type}: {current} >= {limit}"
        self.logger.error(msg)
    
    def log_warning(self, message: str):
        """
        Log a warning.
        
        Args:
            message: Warning message
        """
        self.logger.warning(f"[WARNING] {message}")
    
    def log_error(self, message: str, exception: Exception = None):
        """
        Log an error.
        
        Args:
            message: Error message
            exception: Optional exception object
        """
        if exception:
            self.logger.error(f"[ERROR] {message}", exc_info=exception)
        else:
            self.logger.error(f"[ERROR] {message}")
