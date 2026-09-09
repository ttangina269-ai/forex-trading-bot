# Input Validation Utilities

from typing import Union, List
import re


class Validators:
    """
    Input validation utilities for configuration and parameters.
    """
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """
        Validate currency pair symbol format.
        
        Args:
            symbol: Symbol to validate (e.g., 'EUR/USD' or 'EUR_USD')
            
        Returns:
            True if valid
        """
        # Remove common separators
        clean = symbol.upper().replace("/", "_")
        
        # Should be 3 letter code, separator, 3 letter code
        pattern = r'^[A-Z]{3}_[A-Z]{3}$'
        return bool(re.match(pattern, clean))
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """
        Validate price value.
        
        Args:
            price: Price to validate
            
        Returns:
            True if valid
        """
        return isinstance(price, (int, float)) and price > 0
    
    @staticmethod
    def validate_pips(pips: float) -> bool:
        """
        Validate pip value.
        
        Args:
            pips: Pip value to validate
            
        Returns:
            True if valid
        """
        return isinstance(pips, (int, float)) and pips >= 0
    
    @staticmethod
    def validate_percentage(pct: float) -> bool:
        """
        Validate percentage (0-1 range).
        
        Args:
            pct: Percentage as decimal (0.05 = 5%)
            
        Returns:
            True if valid
        """
        return isinstance(pct, (int, float)) and 0 <= pct <= 1
    
    @staticmethod
    def validate_ratio(ratio: float) -> bool:
        """
        Validate risk/reward ratio.
        
        Args:
            ratio: Ratio value (e.g., 2.0 for 1:2)
            
        Returns:
            True if valid
        """
        return isinstance(ratio, (int, float)) and ratio >= 1.0
    
    @staticmethod
    def validate_period(period: int) -> bool:
        """
        Validate indicator period.
        
        Args:
            period: Period value (candles)
            
        Returns:
            True if valid
        """
        return isinstance(period, int) and period >= 1
    
    @staticmethod
    def validate_symbol_list(symbols: List[str]) -> bool:
        """
        Validate list of currency pair symbols.
        
        Args:
            symbols: List of symbols
            
        Returns:
            True if all valid
        """
        if not isinstance(symbols, list) or len(symbols) == 0:
            return False
        
        return all(Validators.validate_symbol(s) for s in symbols)
    
    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """
        Normalize symbol to standard format.
        
        Args:
            symbol: Input symbol (e.g., 'eur/usd')
            
        Returns:
            Normalized symbol (e.g., 'EUR_USD')
            
        Raises:
            ValueError: If symbol invalid
        """
        normalized = symbol.upper().replace("/", "_")
        
        if not Validators.validate_symbol(normalized):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        return normalized
