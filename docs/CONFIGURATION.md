# Configuration Reference Guide

## Overview

All strategy parameters are defined in `config/config.yaml`. This allows you to:
- Adjust strategy behavior without modifying code
- Test different configurations easily
- Maintain multiple configuration profiles
- Implement walk-forward and out-of-sample testing

## Configuration Structure

### mode
**Type:** string  
**Values:** `paper`, `demo`, `live`  
**Default:** `paper`  
**Description:** Trading mode. Use `paper` or `demo` before going `live`.

```yaml
mode: paper
```

---

## trading

Core trading parameters.

### trading.symbols
**Type:** array of strings  
**Default:** `[EUR/USD, GBP/USD, USD/JPY]`  
**Description:** Currency pairs to trade. Use format with slash: `EUR/USD`

```yaml
trading:
  symbols:
    - EUR/USD
    - GBP/USD
    - USD/JPY
```

### trading.timeframe_entry
**Type:** string  
**Values:** `1m`, `5m`, `15m`, `30m`, `1h`  
**Default:** `15m`  
**Description:** Entry timeframe for signal generation. Typically 15 minutes.

### trading.timeframe_trend
**Type:** string  
**Values:** `1h`, `4h`, `1d`  
**Default:** `1h`  
**Description:** Higher timeframe for trend filtering.

### trading.max_positions
**Type:** integer  
**Default:** `1`  
**Range:** 1-10  
**Description:** Maximum number of simultaneous open positions across all symbols.

### trading.cooldown_minutes
**Type:** integer  
**Default:** `60`  
**Description:** Minimum time (minutes) before entering a new trade in same symbol after closing previous trade.

---

## risk_management

Risk and position management parameters.

### risk_management.risk_per_trade
**Type:** float (0-1)  
**Default:** `0.005`  
**Range:** 0.01% to 10%  
**Description:** Risk per trade as fraction of account equity.
- `0.005` = 0.5% risk per trade
- `0.01` = 1% risk per trade
- Start conservative: 0.25% to 0.5%

```yaml
risk_management:
  risk_per_trade: 0.005  # 0.5% per trade
```

### risk_management.risk_reward_ratio
**Type:** float  
**Default:** `2.0`  
**Range:** 1.0-10.0  
**Description:** Target risk/reward ratio.
- `2.0` = 1:2 ratio (risk 1, target 2 in profit)
- `1.5` = 1:1.5 ratio (tighter targets)
- Minimum of 1:2 recommended for positive expectancy

### risk_management.max_daily_loss_pct
**Type:** float (0-1)  
**Default:** `0.02`  
**Description:** Stop trading for the day if losing this % of equity.
- `0.02` = 2% daily loss limit
- Helps prevent revenge trading

### risk_management.max_weekly_loss_pct
**Type:** float (0-1)  
**Default:** `0.05`  
**Description:** Stop trading for the week if losing this % of equity.
- `0.05` = 5% weekly loss limit

### risk_management.max_drawdown_pct
**Type:** float (0-1)  
**Default:** `0.15`  
**Description:** Stop trading if account drawdown reaches this % of peak equity.
- `0.15` = 15% maximum drawdown
- Once hit, bot stops all new trades until recovery

### risk_management.max_consecutive_losses
**Type:** integer  
**Default:** `5`  
**Description:** Stop trading after this many consecutive losing trades.
- Resets on winning trade
- Helps with psychological control

### risk_management.min_sl_pips
**Type:** float  
**Default:** `5.0`  
**Description:** Skip trade if required stop loss is smaller than this (pips).
- Too-small SL indicates poor signal quality
- Typical range: 5-20 pips

### risk_management.max_sl_pips
**Type:** float  
**Default:** `100.0`  
**Description:** Skip trade if required stop loss exceeds this (pips).
- Too-large SL increases position sizing risk
- Typical range: 50-150 pips

---

## indicators

Indicator calculation parameters.

### indicators.ema_trend
**Type:** integer  
**Default:** `200`  
**Description:** Period for trend EMA on higher timeframe (1H).

### indicators.ema_trend_threshold_pips
**Type:** float  
**Default:** `10.0`  
**Description:** Minimum distance from 200 EMA to have clear bias (pips).
- Prevents trading during indecision
- Increase for more conservative entries (20+ pips)
- Decrease for more aggressive entries (5 pips)

### indicators.ema_fast
**Type:** integer  
**Default:** `20`  
**Description:** Period for fast EMA on entry timeframe (15M).
- Identifies pullback target area
- Typical: 20

### indicators.ema_slow
**Type:** integer  
**Default:** `50`  
**Description:** Period for slow EMA on entry timeframe (15M).
- Identifies pullback target area
- Typical: 50

### indicators.atr_period
**Type:** integer  
**Default:** `14`  
**Description:** Period for ATR volatility calculation.
- Standard: 14
- Shorter (7-10) = more responsive to recent volatility
- Longer (20+) = smoother

### indicators.atr_pullback_distance
**Type:** float  
**Default:** `0.5`  
**Description:** Pullback tolerance as ATR multiple.
- `0.5` = pullback within 0.5 ATR of EMA area
- `0.3` = tighter pullback (more selective)
- `1.0` = wider pullback (more trades)

### indicators.atr_sl_buffer
**Type:** float  
**Default:** `0.0`  
**Description:** Extra SL buffer beyond swing as ATR multiple.
- `0.0` = no buffer (SL exactly at swing)
- `0.5` = add 0.5 ATR below swing (more conservative)
- Increases potential loss but reduces false stops

### indicators.swing_lookback
**Type:** integer  
**Default:** `5`  
**Description:** Number of candles on each side for swing detection.
- `5` = look 5 candles left and right
- `3` = tighter swings (closer SL, smaller stops)
- `7` = wider swings (further SL, larger stops)

---

## entry_confirmation

Entry pattern confirmation settings.

### entry_confirmation.enable_engulfing
**Type:** boolean  
**Default:** `true`  
**Description:** Enable engulfing candle confirmation patterns.

### entry_confirmation.enable_rejection
**Type:** boolean  
**Default:** `true`  
**Description:** Enable rejection candle confirmation patterns.

### entry_confirmation.rejection_wick_ratio
**Type:** float  
**Default:** `1.5`  
**Description:** Minimum wick/body ratio for rejection pattern.
- `1.5` = wick must be 1.5x body size
- `2.0` = require stronger rejection (fewer trades)
- `1.0` = accept any wick (more trades, potentially lower quality)

---

## filters

Trade filtering parameters.

### filters.max_spread_pips
**Type:** float  
**Default:** `1.5`  
**Description:** Skip trade if bid-ask spread exceeds this (pips).
- Wider spreads during low liquidity
- Typical ranges:
  - Major pairs (EUR/USD): 0.5-1.5 pips
  - Minor pairs (GBP/USD): 1-2 pips
  - Exotic pairs: 2-5 pips

### filters.min_atr_pips
**Type:** float  
**Default:** `0.0`  
**Description:** Skip trade if ATR is below this (pips). Set 0 to disable.
- `0.0` = no minimum (all volatility levels)
- `5.0` = require at least 5 pips volatility
- Useful in low-volatility environments

### filters.max_atr_pips
**Type:** float  
**Default:** `0.0`  
**Description:** Skip trade if ATR exceeds this (pips). Set 0 to disable.
- `0.0` = no maximum (all volatility levels)
- `100.0` = skip if volatility too high
- Prevents trading during high-risk periods (news, etc.)

### filters.trading_sessions
**Type:** array of strings  
**Values:** `london`, `newyork`, `tokyo`, `sydney`, `all`  
**Default:** `[london, newyork]`  
**Description:** Trading session windows (UTC).

```yaml
filters:
  trading_sessions:
    - london    # 08:00-17:00 UTC
    - newyork   # 13:00-22:00 UTC
```

Session times (UTC):
- **London:** 08:00 - 17:00 (8 hours)
- **New York:** 13:00 - 22:00 (9 hours)
- **Tokyo:** 21:00 - 06:00 UTC next day (9 hours)
- **Sydney:** 22:00 - 07:00 UTC next day (9 hours)

### filters.trading_days
**Type:** array of strings  
**Values:** `monday`, `tuesday`, `wednesday`, `thursday`, `friday`  
**Default:** `[monday, tuesday, wednesday, thursday, friday]`  
**Description:** Days of week to allow trading.

```yaml
filters:
  trading_days:
    - monday
    - tuesday
    - wednesday
    - thursday
    - friday
    # Skips Saturday and Sunday (weekends)
```

---

## trade_management

Optional advanced trade management features.

**Default:** All disabled. Enable only after thorough testing.

### trade_management.enable_breakeven
**Type:** boolean  
**Default:** `false`  
**Description:** Move stop loss to entry price after specified profit.

### trade_management.breakeven_after_r
**Type:** float  
**Default:** `1.0`  
**Description:** Move to breakeven after this many R of profit.
- Locks in minimal profit (commission + spread)

### trade_management.enable_partial_profit
**Type:** boolean  
**Default:** `false`  
**Description:** Enable partial profit taking at defined levels.

### trade_management.partial_profit_levels
**Type:** array  
**Description:** Define profit-taking levels.

```yaml
trade_management:
  enable_partial_profit: false
  partial_profit_levels:
    - r_level: 1.0      # At 1R profit
      quantity_pct: 0.5  # Take 50% off
    - r_level: 2.0      # At 2R profit
      quantity_pct: 0.5  # Take rest
```

### trade_management.enable_trailing_stop
**Type:** boolean  
**Default:** `false`  
**Description:** Enable trailing stop (fixed pips).

### trade_management.trailing_stop_pips
**Type:** float  
**Description:** Trailing stop distance in pips.

### trade_management.enable_atr_trailing_stop
**Type:** boolean  
**Default:** `false`  
**Description:** Enable ATR-based trailing stop.

### trade_management.atr_trailing_multiplier
**Type:** float  
**Default:** `1.0`  
**Description:** Trailing stop = ATR × this multiplier.

---

## logging

Logging configuration.

### logging.log_level
**Type:** string  
**Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`  
**Default:** `INFO`  
**Description:** Logging verbosity.
- `DEBUG`: Very detailed (development)
- `INFO`: Normal (production)
- `WARNING`: Only problems
- `ERROR`: Only critical errors

### logging.log_to_file
**Type:** boolean  
**Default:** `true`  
**Description:** Write logs to file (logs/)

### logging.log_to_console
**Type:** boolean  
**Default:** `true`  
**Description:** Display logs on console

---

## Configuration Examples

### Conservative (Low Risk)

```yaml
mode: paper

trading:
  symbols: [EUR/USD]
  max_positions: 1
  cooldown_minutes: 120

risk_management:
  risk_per_trade: 0.002    # 0.2%
  risk_reward_ratio: 2.5
  max_drawdown_pct: 0.10   # 10%
  max_consecutive_losses: 3
  min_sl_pips: 10
  max_sl_pips: 50

indicators:
  ema_trend_threshold_pips: 15
  atr_pullback_distance: 0.3

filters:
  max_spread_pips: 1.0
  min_atr_pips: 5
```

### Aggressive (Higher Risk)

```yaml
mode: paper

trading:
  symbols: [EUR/USD, GBP/USD, USD/JPY]
  max_positions: 3
  cooldown_minutes: 30

risk_management:
  risk_per_trade: 0.01     # 1.0%
  risk_reward_ratio: 1.5
  max_drawdown_pct: 0.25   # 25%
  max_consecutive_losses: 7
  min_sl_pips: 5
  max_sl_pips: 150

indicators:
  ema_trend_threshold_pips: 5
  atr_pullback_distance: 1.0

filters:
  max_spread_pips: 2.0
```

---

## Configuration Validation

Before running, verify your config is valid:

```bash
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

Should complete without errors.

## Configuration Best Practices

1. **Start Conservative:** Begin with paper_trading.yaml template
2. **Test Each Change:** Modify one parameter at a time
3. **Backtest First:** Test config changes on historical data
4. **Walk-Forward Test:** Test on data the strategy hasn't seen
5. **Document Changes:** Note why you changed each parameter
6. **Avoid Over-Optimization:** Use reasonable ranges, not extreme values
7. **Monitor Live:** Track paper trading performance for 2+ weeks
