# Backtesting Engine - Historical data simulation

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    """Record of a trade during backtesting."""
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_time: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_amount: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None  # "TP", "SL", "MANUAL"
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    r_value: Optional[float] = None  # Profit/loss in risk units
    duration: Optional[timedelta] = None
    
    def __post_init__(self):
        """Calculate values after initialization."""
        if self.exit_time and self.entry_time:
            self.duration = self.exit_time - self.entry_time


@dataclass
class BacktestStats:
    """Complete backtesting statistics."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    
    average_win: float = 0.0
    average_loss: float = 0.0
    average_r_win: float = 0.0  # Average win in R units
    average_r_loss: float = 0.0  # Average loss in R units
    
    profit_factor: float = 0.0  # Gross profit / Gross loss
    expectancy_per_trade: float = 0.0  # Average P&L per trade
    
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    
    average_trade_duration: timedelta = field(default_factory=timedelta)
    
    best_trade: Optional[BacktestTrade] = None
    worst_trade: Optional[BacktestTrade] = None
    
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    yearly_returns: Dict[int, float] = field(default_factory=dict)


class BacktestEngine:
    """
    Backtesting engine for testing strategy on historical data.
    
    Simulates trading based on historical OHLC data with realistic
    spread, commission, and slippage.
    """
    
    def __init__(
        self,
        starting_equity: float = 100000.0,
        spread_pips: float = 1.5,
        commission_per_trade: float = 5.0,  # USD
        slippage_pips: float = 0.5
    ):
        """
        Args:
            starting_equity: Initial account balance
            spread_pips: Average spread in pips
            commission_per_trade: Commission per trade in USD
            slippage_pips: Average slippage in pips
        """
        self.starting_equity = starting_equity
        self.current_equity = starting_equity
        self.peak_equity = starting_equity
        
        self.spread_pips = spread_pips
        self.commission_per_trade = commission_per_trade
        self.slippage_pips = slippage_pips
        
        self.trades: List[BacktestTrade] = []
        self.equity_history: List[Tuple[datetime, float]] = []
    
    def add_trade(self, trade: BacktestTrade):
        """
        Add a completed trade and update equity.
        
        Args:
            trade: BacktestTrade object with entry and exit data
        """
        if not trade.exit_price or not trade.exit_time:
            raise ValueError("Trade must be closed before adding to results")
        
        # Calculate P&L
        if trade.direction == "LONG":
            pnl = (trade.exit_price - trade.entry_price) * trade.position_size
        else:  # SHORT
            pnl = (trade.entry_price - trade.exit_price) * trade.position_size
        
        # Apply costs
        pnl -= self.commission_per_trade
        pnl -= (self.spread_pips * 0.0001 * trade.position_size * 100000)  # Spread cost
        
        trade.pnl = pnl
        trade.pnl_pct = pnl / self.current_equity * 100
        
        # Calculate R value (profit/loss in risk units)
        risk_amount = trade.risk_amount
        if risk_amount > 0:
            trade.r_value = pnl / risk_amount
        
        # Update equity
        self.current_equity += pnl
        
        # Track peak equity for drawdown calculation
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity
        
        self.trades.append(trade)
        
        logger.debug(
            f"Trade closed: {trade.symbol} {trade.direction} | "
            f"P&L: ${pnl:.2f} ({trade.pnl_pct:+.2f}%) | "
            f"Equity: ${self.current_equity:.2f}"
        )
    
    def calculate_stats(self) -> BacktestStats:
        """
        Calculate comprehensive backtest statistics.
        
        Returns:
            BacktestStats object with all metrics
        """
        if not self.trades:
            return BacktestStats()
        
        stats = BacktestStats()
        stats.total_trades = len(self.trades)
        
        # Count wins and losses
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        
        stats.winning_trades = len(winning_trades)
        stats.losing_trades = len(losing_trades)
        stats.win_rate = stats.winning_trades / stats.total_trades if stats.total_trades > 0 else 0.0
        
        # P&L calculations
        stats.total_pnl = sum(t.pnl for t in self.trades)
        stats.total_pnl_pct = (stats.total_pnl / self.starting_equity) * 100
        
        # Average win/loss
        if winning_trades:
            stats.average_win = sum(t.pnl for t in winning_trades) / len(winning_trades)
            stats.average_r_win = sum(t.r_value for t in winning_trades if t.r_value) / len(winning_trades)
        
        if losing_trades:
            stats.average_loss = sum(t.pnl for t in losing_trades) / len(losing_trades)
            stats.average_r_loss = sum(t.r_value for t in losing_trades if t.r_value) / len(losing_trades)
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        if gross_loss > 0:
            stats.profit_factor = gross_profit / gross_loss
        
        # Expectancy
        stats.expectancy_per_trade = stats.total_pnl / stats.total_trades if stats.total_trades > 0 else 0.0
        
        # Drawdown
        current_peak = self.starting_equity
        max_dd = 0.0
        
        for _, equity in self.equity_history:
            if equity > current_peak:
                current_peak = equity
            
            dd = (current_peak - equity) / current_peak
            if dd > max_dd:
                max_dd = dd
        
        stats.max_drawdown_pct = max_dd * 100
        stats.max_drawdown = max_dd * current_peak
        
        # Trade duration
        if self.trades:
            total_duration = sum(
                (t.exit_time - t.entry_time).total_seconds() 
                for t in self.trades if t.duration
            )
            avg_duration_seconds = total_duration / stats.total_trades
            stats.average_trade_duration = timedelta(seconds=avg_duration_seconds)
        
        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        
        for trade in self.trades:
            if trade.pnl > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                stats.max_consecutive_wins = max(stats.max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                stats.max_consecutive_losses = max(stats.max_consecutive_losses, consecutive_losses)
        
        # Best and worst trades
        if self.trades:
            stats.best_trade = max(self.trades, key=lambda t: t.pnl or 0)
            stats.worst_trade = min(self.trades, key=lambda t: t.pnl or 0)
        
        # Monthly and yearly returns
        for trade in self.trades:
            if trade.exit_time:
                month_key = trade.exit_time.strftime('%Y-%m')
                stats.monthly_returns[month_key] = stats.monthly_returns.get(month_key, 0.0) + (trade.pnl or 0)
                
                year_key = trade.exit_time.year
                stats.yearly_returns[year_key] = stats.yearly_returns.get(year_key, 0.0) + (trade.pnl or 0)
        
        return stats
    
    def print_report(self):
        """
        Print detailed backtest report.
        """
        stats = self.calculate_stats()
        
        print("\n" + "="*80)
        print("BACKTESTING REPORT")
        print("="*80)
        
        print(f"\nStarting Equity: ${self.starting_equity:,.2f}")
        print(f"Final Equity: ${self.current_equity:,.2f}")
        print(f"Total P&L: ${stats.total_pnl:,.2f} ({stats.total_pnl_pct:+.2f}%)")
        
        print(f"\n--- Trade Statistics ---")
        print(f"Total Trades: {stats.total_trades}")
        print(f"Winning Trades: {stats.winning_trades} ({stats.win_rate*100:.1f}%)")
        print(f"Losing Trades: {stats.losing_trades} ({(1-stats.win_rate)*100:.1f}%)")
        
        print(f"\n--- Risk/Reward Analysis ---")
        print(f"Average Win: ${stats.average_win:,.2f} ({stats.average_r_win:+.2f}R)")
        print(f"Average Loss: ${stats.average_loss:,.2f} ({stats.average_r_loss:+.2f}R)")
        print(f"Profit Factor: {stats.profit_factor:.2f}")
        print(f"Expectancy per Trade: ${stats.expectancy_per_trade:,.2f}")
        
        print(f"\n--- Drawdown & Duration ---")
        print(f"Max Drawdown: {stats.max_drawdown_pct:.2f}%")
        print(f"Average Trade Duration: {stats.average_trade_duration}")
        print(f"Max Consecutive Losses: {stats.max_consecutive_losses}")
        
        if stats.best_trade:
            print(f"\nBest Trade: {stats.best_trade.symbol} {stats.best_trade.direction} +${stats.best_trade.pnl:,.2f}")
        
        if stats.worst_trade:
            print(f"Worst Trade: {stats.worst_trade.symbol} {stats.worst_trade.direction} -${abs(stats.worst_trade.pnl):,.2f}")
        
        print("\n" + "="*80 + "\n")
