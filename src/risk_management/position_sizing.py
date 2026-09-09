# Position Sizing - Dynamic calculation based on risk

from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PositionSize:
    """Position sizing calculation result."""
    lot_size: float
    risk_amount: float
    sl_distance_pips: float
    entry_price: float
    stop_loss: float
    currency: str
    
    def __str__(self) -> str:
        return (
            f"Position Size: {self.lot_size:.2f} lots | "
            f"Risk: ${self.risk_amount:.2f} | "
            f"SL Distance: {self.sl_distance_pips:.1f} pips"
        )


class PositionSizer:
    """
    Calculate dynamic position size based on account equity and risk.
    
    Formula:
    - Risk Amount = Account Equity × Risk Percentage
    - Lot Size = Risk Amount / (SL Distance in Pips × Pip Value per Lot)
    
    This ensures every trade risks the same dollar amount regardless of
    volatility, market conditions, or currency pair characteristics.
    """
    
    # Pip values per standard lot for common pairs
    # These are standard for OANDA and most brokers
    PIP_VALUES = {
        "EUR_USD": 10.0,   # $10 per pip per standard lot
        "GBP_USD": 10.0,   # $10 per pip
        "USD_JPY": 1000.0, # ¥1000 per pip (needs conversion to USD)
        "AUD_USD": 10.0,
        "NZD_USD": 10.0,
        "USD_CAD": 10.0,
        "USD_CHF": 10.0,
    }
    
    def __init__(self, pip_value_override: dict = None):
        """
        Args:
            pip_value_override: Custom pip values for pairs
        """
        self.pip_values = self.PIP_VALUES.copy()
        if pip_value_override:
            self.pip_values.update(pip_value_override)
    
    def get_pip_value(self, symbol: str) -> float:
        """
        Get pip value for a currency pair.
        
        Args:
            symbol: Symbol in format "EUR_USD"
            
        Returns:
            Pip value per standard lot (100,000 units)
            
        Raises:
            ValueError: If symbol not found
        """
        # Remove slash if present (EUR/USD -> EUR_USD)
        symbol = symbol.upper().replace("/", "_")
        
        if symbol not in self.pip_values:
            raise ValueError(f"Unknown symbol: {symbol}")
        
        return self.pip_values[symbol]
    
    def calculate_position_size(
        self,
        account_equity: float,
        risk_percent: float,
        sl_distance_pips: float,
        symbol: str,
        entry_price: float,
        stop_loss: float,
        min_lot_size: float = 0.01,
        max_lot_size: float = 100.0
    ) -> PositionSize:
        """
        Calculate position size for a trade.
        
        Args:
            account_equity: Current account equity in USD
            risk_percent: Risk per trade (0.005 = 0.5%)
            sl_distance_pips: Stop loss distance in pips
            symbol: Currency pair (EUR_USD)
            entry_price: Entry price
            stop_loss: Stop loss price
            min_lot_size: Minimum lot size (default 0.01)
            max_lot_size: Maximum lot size (default 100)
            
        Returns:
            PositionSize object
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if account_equity <= 0:
            raise ValueError(f"Account equity must be > 0: {account_equity}")
        
        if not 0.0001 <= risk_percent <= 0.50:
            raise ValueError(f"Risk percent must be 0.01% to 50%: {risk_percent}")
        
        if sl_distance_pips <= 0:
            raise ValueError(f"SL distance must be > 0: {sl_distance_pips}")
        
        # 1. Calculate maximum risk in account currency
        risk_amount = account_equity * risk_percent
        
        logger.debug(
            f"Position Sizing: "
            f"Equity=${account_equity}, Risk%={risk_percent*100:.2f}%, "
            f"Risk Amount=${risk_amount:.2f}"
        )
        
        # 2. Get pip value for this symbol
        try:
            pip_value = self.get_pip_value(symbol)
        except ValueError as e:
            logger.error(f"Position sizing failed: {e}")
            raise
        
        # 3. Calculate total cost of SL distance
        sl_cost_per_lot = sl_distance_pips * pip_value
        
        if sl_cost_per_lot <= 0:
            raise ValueError(
                f"Invalid SL cost calculation: "
                f"{sl_distance_pips} pips × {pip_value} = {sl_cost_per_lot}"
            )
        
        # 4. Calculate lot size
        lot_size = risk_amount / sl_cost_per_lot
        
        logger.debug(
            f"Lot Calculation: "
            f"${risk_amount:.2f} / ({sl_distance_pips} pips × {pip_value}) = {lot_size:.3f} lots"
        )
        
        # 5. Apply constraints
        original_lot_size = lot_size
        lot_size = max(min_lot_size, min(lot_size, max_lot_size))
        
        if lot_size != original_lot_size:
            logger.warning(
                f"Lot size constrained: {original_lot_size:.3f} -> {lot_size:.3f} "
                f"(min={min_lot_size}, max={max_lot_size})"
            )
        
        # 6. Round to broker precision (typically 0.01)
        lot_size = round(lot_size, 2)
        
        if lot_size < min_lot_size:
            raise ValueError(
                f"Calculated lot size {lot_size} < minimum {min_lot_size}"
            )
        
        # Recalculate actual risk amount based on rounded lot size
        actual_risk = lot_size * sl_distance_pips * pip_value
        
        result = PositionSize(
            lot_size=lot_size,
            risk_amount=actual_risk,
            sl_distance_pips=sl_distance_pips,
            entry_price=entry_price,
            stop_loss=stop_loss,
            currency=symbol.split("_")[1]  # Get quote currency
        )
        
        logger.info(f"Position Size: {result}")
        
        return result
