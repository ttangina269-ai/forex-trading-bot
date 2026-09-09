# Unit tests for position sizing

import pytest
from src.risk_management.position_sizing import PositionSizer, PositionSize


class TestPositionSizer:
    """Test dynamic position sizing."""
    
    def test_position_sizer_initialization(self):
        """Test position sizer initialization."""
        sizer = PositionSizer()
        
        # Check default pip values are loaded
        assert sizer.get_pip_value("EUR_USD") == 10.0
        assert sizer.get_pip_value("GBP_USD") == 10.0
        assert sizer.get_pip_value("USD_JPY") == 1000.0
    
    def test_position_sizer_custom_pip_values(self):
        """Test position sizer with custom pip values."""
        custom_pips = {"EUR_USD": 5.0}
        sizer = PositionSizer(pip_value_override=custom_pips)
        
        assert sizer.get_pip_value("EUR_USD") == 5.0
        assert sizer.get_pip_value("GBP_USD") == 10.0  # Default still works
    
    def test_get_pip_value_symbol_formats(self):
        """Test pip value retrieval with different symbol formats."""
        sizer = PositionSizer()
        
        # Test with slash
        assert sizer.get_pip_value("EUR/USD") == 10.0
        
        # Test with underscore
        assert sizer.get_pip_value("EUR_USD") == 10.0
        
        # Test lowercase
        assert sizer.get_pip_value("eur_usd") == 10.0
    
    def test_get_pip_value_unknown_symbol(self):
        """Test error with unknown symbol."""
        sizer = PositionSizer()
        
        with pytest.raises(ValueError):
            sizer.get_pip_value("XXX_YYY")
    
    def test_calculate_position_size_basic(self):
        """Test basic position size calculation."""
        sizer = PositionSizer()
        
        result = sizer.calculate_position_size(
            account_equity=100000.0,
            risk_percent=0.005,  # 0.5%
            sl_distance_pips=20.0,
            symbol="EUR_USD",
            entry_price=1.1000,
            stop_loss=1.0980,
            min_lot_size=0.01,
            max_lot_size=100.0
        )
        
        # Risk = 100,000 * 0.005 = 500
        # Lot Size = 500 / (20 * 10) = 500 / 200 = 2.5
        assert result.lot_size == 2.5
        assert result.risk_amount == 500.0
        assert result.sl_distance_pips == 20.0
    
    def test_calculate_position_size_example_eur_usd(self):
        """Test real example: EUR/USD with 0.5% risk, 20 pips SL."""
        sizer = PositionSizer()
        
        result = sizer.calculate_position_size(
            account_equity=50000.0,
            risk_percent=0.005,  # 0.5%
            sl_distance_pips=20.0,
            symbol="EUR_USD",
            entry_price=1.1000,
            stop_loss=1.0980,
            min_lot_size=0.01,
            max_lot_size=100.0
        )
        
        # Risk = 50,000 * 0.005 = 250
        # Lot Size = 250 / (20 * 10) = 250 / 200 = 1.25
        assert result.lot_size == 1.25
        assert result.risk_amount == 250.0
    
    def test_calculate_position_size_jpy_pair(self):
        """Test position sizing with JPY pair (different pip value)."""
        sizer = PositionSizer()
        
        result = sizer.calculate_position_size(
            account_equity=100000.0,
            risk_percent=0.005,
            sl_distance_pips=20.0,
            symbol="USD_JPY",
            entry_price=150.00,
            stop_loss=149.80,
            min_lot_size=0.01,
            max_lot_size=100.0
        )
        
        # Risk = 100,000 * 0.005 = 500
        # Lot Size = 500 / (20 * 1000) = 500 / 20000 = 0.025
        assert result.lot_size == 0.03  # Rounded to 0.01 precision
        assert result.currency == "JPY"
    
    def test_calculate_position_size_with_constraints(self):
        """Test lot size constrained by min/max."""
        sizer = PositionSizer()
        
        # Very small SL = very large lot size
        result = sizer.calculate_position_size(
            account_equity=100000.0,
            risk_percent=0.005,
            sl_distance_pips=1.0,  # Very small
            symbol="EUR_USD",
            entry_price=1.1000,
            stop_loss=1.0999,
            min_lot_size=0.01,
            max_lot_size=10.0  # Constrain to max 10
        )
        
        # Calculated: 500 / (1 * 10) = 50 lots
        # But constrained to max 10
        assert result.lot_size == 10.0
    
    def test_calculate_position_size_invalid_equity(self):
        """Test error with invalid account equity."""
        sizer = PositionSizer()
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                account_equity=0,
                risk_percent=0.005,
                sl_distance_pips=20.0,
                symbol="EUR_USD",
                entry_price=1.1000,
                stop_loss=1.0980
            )
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                account_equity=-100000,
                risk_percent=0.005,
                sl_distance_pips=20.0,
                symbol="EUR_USD",
                entry_price=1.1000,
                stop_loss=1.0980
            )
    
    def test_calculate_position_size_invalid_risk_percent(self):
        """Test error with invalid risk percent."""
        sizer = PositionSizer()
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                account_equity=100000,
                risk_percent=0.0,  # Must be > 0
                sl_distance_pips=20.0,
                symbol="EUR_USD",
                entry_price=1.1000,
                stop_loss=1.0980
            )
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                account_equity=100000,
                risk_percent=1.0,  # Must be <= 0.5 (50%)
                sl_distance_pips=20.0,
                symbol="EUR_USD",
                entry_price=1.1000,
                stop_loss=1.0980
            )
    
    def test_calculate_position_size_invalid_sl_distance(self):
        """Test error with invalid SL distance."""
        sizer = PositionSizer()
        
        with pytest.raises(ValueError):
            sizer.calculate_position_size(
                account_equity=100000,
                risk_percent=0.005,
                sl_distance_pips=0,  # Must be > 0
                symbol="EUR_USD",
                entry_price=1.1000,
                stop_loss=1.1000
            )
