# Forex Trading Bot - Mechanical Strategy System

## Overview

A fully automated, rule-based forex trading system designed for robust long-term expectancy with strict drawdown controls. This bot implements a mechanical pullback trading strategy on multiple currency pairs using multi-timeframe analysis.

**Key Design Principle:** Positive long-term expectancy with controlled drawdown, NOT maximum win rate.

## Strategy Summary

### Timeframes
- **1H Chart:** Trend direction filter using 200 EMA
- **15M Chart:** Entry identification using 20 EMA and 50 EMA pullbacks with price-action confirmation

### Core Rules

1. **Trend Filter (1H):**
   - LONG bias: 1H close > 1H 200 EMA
   - SHORT bias: 1H close < 1H 200 EMA
   - No trade if price is extremely close to 200 EMA

2. **Pullback Detection (15M):**
   - Price must pull back toward 20/50 EMA area
   - Pullback must not invalidate higher-timeframe trend
   - ATR-based distance for volatility adaptation

3. **Entry Confirmation:**
   - Bullish/bearish engulfing candles
   - Strong rejection candles
   - Mathematically defined, deterministic patterns

4. **Entry:**
   - Market order immediately after confirmation candle closes
   - One position per symbol
   - Configurable cooldown after trade closure

5. **Risk/Reward:**
   - Default 1:2 ratio
   - Stop below swing low (LONG) or above swing high (SHORT)
   - Mechanical swing detection (configurable lookback)

6. **Position Sizing:**
   - Dynamic sizing based on account equity, risk %, SL distance
   - Default 0.5% risk per trade
   - No fixed lot sizes

7. **Risk Controls:**
   - Maximum daily/weekly loss
   - Maximum drawdown
   - Maximum consecutive losses
   - No martingale, grid, or revenge trading

### Supported Symbols
- EUR/USD
- GBP/USD
- USD/JPY
- Configurable for additional pairs

### Trade Filters
- Maximum spread
- Trading session (London, New York)
- Minimum/maximum ATR volatility
- Day of week
- Daylight-saving-time handling

## Project Structure

```
forex-trading-bot/
├── config/
│   ├── config.yaml              # Main configuration file
│   ├── config.schema.json       # Configuration validation schema
│   └── example_configs/         # Example configurations
│       ├── conservative.yaml
│       ├── aggressive.yaml
│       └── paper_trading.yaml
├── src/
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── bot.py                   # Main bot orchestrator
│   ├── indicators/
│   │   ├── __init__.py
│   │   ├── ema.py              # Exponential Moving Average
│   │   ├── atr.py              # Average True Range
│   │   └── swings.py           # Swing high/low detection
│   ├── signals/
│   │   ├── __init__.py
│   │   ├── trend_filter.py     # 1H trend analysis
│   │   ├── pullback.py         # 15M pullback detection
│   │   ├── confirmation.py     # Entry confirmation patterns
│   │   └── signal_generator.py # Combined signal logic
│   ├── risk_management/
│   │   ├── __init__.py
│   │   ├── position_sizing.py  # Dynamic position calculation
│   │   ├── risk_validator.py   # Trade filter validation
│   │   └── drawdown_manager.py # Drawdown tracking
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_provider.py    # Abstract data interface
│   │   ├── oanda_provider.py   # OANDA API implementation
│   │   └── cache.py            # Data caching
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── broker.py           # Abstract broker interface
│   │   ├── oanda_broker.py     # OANDA broker implementation
│   │   └── order_manager.py    # Order execution and management
│   ├── state/
│   │   ├── __init__.py
│   │   └── persistence.py      # Trade state storage
│   ├── logger/
│   │   ├── __init__.py
│   │   └── trade_logger.py     # Comprehensive trade logging
│   └── utils/
│       ├── __init__.py
│       ├── time_utils.py       # DST and session handling
│       └── validators.py       # Input validation
├── backtesting/
│   ├── __init__.py
│   ├── backtest_engine.py      # Core backtesting engine
│   ├── data_loader.py          # Historical data loading
│   ├── reporter.py             # Backtest report generation
│   └── monte_carlo.py          # Monte Carlo analysis
├── tests/
│   ├── __init__.py
│   ├── test_indicators.py
│   ├── test_signals.py
│   ├── test_position_sizing.py
│   ├── test_risk_validation.py
│   ├── test_confirmation.py
│   └── test_integration.py
├── docs/
│   ├── STRATEGY_RULES.md       # Detailed strategy documentation
│   ├── INSTALLATION.md         # Setup instructions
│   ├── BACKTESTING.md          # Backtesting guide
│   ├── PAPER_TRADING.md        # Paper trading setup
│   ├── LIVE_TRADING.md         # Live trading guide
│   └── CONFIGURATION.md        # Configuration reference
├── examples/
│   └── sample_backtest_report.md
├── requirements.txt
├── setup.py
└── .env.example
```

## Quick Start

### Installation

```bash
git clone https://github.com/ttangina269-ai/forex-trading-bot.git
cd forex-trading-bot
pip install -r requirements.txt
```

### Configuration

1. Copy configuration template:
   ```bash
   cp config/example_configs/paper_trading.yaml config/config.yaml
   ```

2. Edit `config/config.yaml` with your settings

3. Set environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

### Paper Trading

```bash
python src/main.py --mode paper
```

### Backtesting

```bash
python src/main.py --mode backtest --from 2023-01-01 --to 2024-01-01
```

### Running Tests

```bash
pytest tests/ -v
```

## Key Features

✅ **Mechanical Signal Generation**
- Deterministic, testable patterns
- No subjective interpretation
- Reproducible across multiple runs

✅ **Dynamic Position Sizing**
- Calculated from account equity, risk %, and SL distance
- Adapts to market volatility
- No fixed lot sizes

✅ **Comprehensive Risk Management**
- Daily/weekly/monthly loss limits
- Maximum drawdown controls
- Consecutive loss tracking
- Kill-switch safety mechanisms

✅ **Anti-Overfitting Safeguards**
- In-sample/out-of-sample separation
- Walk-forward testing
- Monte Carlo analysis
- Reasonable parameter ranges

✅ **Robust Backtesting**
- Spread, commission, slippage simulation
- Complete trade statistics
- Risk-adjusted metrics (Sharpe, Sortino)
- Monthly/yearly performance breakdown

✅ **Detailed Logging**
- Every trade decision logged
- Rejection reasons documented
- Setup details recorded
- Performance tracking

✅ **Safety First**
- Defaults to DEMO/PAPER mode
- Connection monitoring
- Data staleness detection
- Multiple validation layers

## Strategy Expectations

**This is NOT a guaranteed profit system.** The strategy aims to:

1. Achieve positive expectancy after realistic transaction costs
2. Limit drawdown to acceptable levels
3. Maintain performance across different market regimes
4. Avoid overfitting to historical data

Success is measured by:
- Consistent positive expectancy (not win rate)
- Acceptable maximum drawdown
- Out-of-sample validation
- Long-term survival and profitability

## Documentation

See `docs/` directory for:
- Detailed strategy rules and justification
- Installation and setup guide
- Backtesting methodology
- Paper trading procedures
- Live trading deployment checklist
- Configuration reference

## Development Status

This is a **work in progress**. Current status:
- ✅ Core indicator calculations
- ✅ Signal generation logic
- ✅ Position sizing
- ✅ Risk management framework
- ✅ Backtesting engine
- ✅ Unit tests
- 🔄 Live broker integration (OANDA)
- 🔄 Paper trading mode
- ⏳ Monte Carlo analysis

## Safety & Disclaimer

**Important:**

1. This bot defaults to **DEMO/PAPER mode**. Enable live trading only after:
   - Extensive backtesting
   - Successful paper trading validation
   - Out-of-sample testing
   - Manual review and approval

2. Past performance does not guarantee future results.

3. Forex trading involves risk. You can lose your investment.

4. Always use risk management and position sizing.

5. Run a paper-trading phase with real market conditions before deploying capital.

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome. Please ensure:
- All new code includes unit tests
- Configuration changes are backward compatible
- Risk management logic is not modified without extensive testing
- Changes follow the modular architecture

## Support

For issues, questions, or improvements, please open a GitHub issue.
