# Strategy Rules - Detailed Mechanical Definitions

## 1. Trend Filter (1H Timeframe)

### Objective
Determine whether we have a LONG bias, SHORT bias, or NO TRADE condition.

### Rule
Calculate the 200-period EMA on the 1H chart. Compare the most recent 1H closing price to this EMA.

**LONG BIAS:**
```
if close_1h > ema_200_1h + threshold:
    bias = LONG
```

**SHORT BIAS:**
```
if close_1h < ema_200_1h - threshold:
    bias = SHORT
```

**NO TRADE:**
```
if abs(close_1h - ema_200_1h) <= threshold:
    bias = NO_TRADE
```

Where `threshold` is a configurable value (default: 10 pips) to avoid trading extremely close to the 200 EMA, which indicates indecision.

### Rationale
- The 200 EMA is a standard long-term trend indicator in forex
- Closing price relationship to the EMA confirms trend direction
- Threshold prevents trading during consolidation/indecision
- This acts as a market regime filter; only trade when trend is clear

### Implementation Note
The 200 EMA must be recalculated on every new 1H candle close. Cache the result for the current 1H candle and re-evaluate only when a new 1H candle opens.

---

## 2. Pullback Detection (15M Timeframe)

### Objective
Identify when price pulls back toward key moving averages (20/50 EMA) after establishing a higher-timeframe trend.

### Setup
On the 15M chart, calculate:
- 20-period EMA (fast MA)
- 50-period EMA (slow MA)
- 14-period ATR (volatility measure)

### LONG Pullback Condition
```
1. Trend bias must be LONG (from 1H filter)
2. Price must be within pullback_distance of the EMA area:
   - pullback_distance = ATR * atr_pullback_distance (default: 0.5 ATR)
   - "EMA area" = [min(EMA20, EMA50), max(EMA20, EMA50)]
3. Current price < highest high of last N candles (optional: pullback occurred)
4. Pullback must not close below EMA50 (validates trend is intact)
```

### SHORT Pullback Condition
```
1. Trend bias must be SHORT (from 1H filter)
2. Price must be within pullback_distance of the EMA area:
   - pullback_distance = ATR * atr_pullback_distance (default: 0.5 ATR)
   - "EMA area" = [min(EMA20, EMA50), max(EMA20, EMA50)]
3. Current price > lowest low of last N candles (optional: pullback occurred)
4. Pullback must not close above EMA50 (validates trend is intact)
```

### Mathematical Definition

**Pullback Distance Calculation:**
```python
atr_value = calculate_atr(14)  # 14-period ATR on 15M
pullback_distance = atr_value * 0.5  # 0.5 ATR (configurable)

ema_20 = calculate_ema(20)
ema_50 = calculate_ema(50)

ema_min = min(ema_20, ema_50)
ema_max = max(ema_20, ema_50)

# LONG: Price touches support at EMA area
if ema_min - pullback_distance <= close <= ema_min + pullback_distance:
    pullback_detected = True

# SHORT: Price touches resistance at EMA area
if ema_max - pullback_distance <= close <= ema_max + pullback_distance:
    pullback_detected = True
```

### Rationale
- The 20/50 EMA pair identifies the current momentum zone
- Pullbacks toward EMAs are natural support/resistance in trending markets
- ATR-based distance adapts to volatility changes between pairs
- Validates that trend is intact by checking EMA structure

### Implementation Note
- Only evaluate pullback on CLOSED 15M candles
- Never use unfinished candle data for entry decisions
- Pullback conditions must be checked fresh on every new 15M close

---

## 3. Price-Action Confirmation (15M Timeframe)

### Objective
Confirm that price is ready to reverse from pullback and move in the direction of the higher-timeframe bias.

### Confirmation Patterns

#### Bullish Engulfing (for LONG entries)

**Definition:**
```
1. Previous candle (N-1) is bearish:
   - close[N-1] < open[N-1]

2. Current candle (N) is bullish:
   - close[N] > open[N]

3. Current candle completely engulfs previous candle body:
   - open[N] < open[N-1]    # Opens below or at previous open
   - close[N] > close[N-1]  # Closes above previous close

4. Current candle closes well above previous candle:
   - (close[N] - open[N]) > (open[N-1] - close[N-1])  # Current body larger
   - close[N] > open[N-1]   # Closes above previous open
```

**Pseudocode:**
```python
def is_bullish_engulfing(prev_candle, curr_candle):
    # Previous must be bearish
    if not (prev_candle.close < prev_candle.open):
        return False
    
    # Current must be bullish
    if not (curr_candle.close > curr_candle.open):
        return False
    
    # Current opens below previous and closes above previous close
    if not (curr_candle.open <= prev_candle.open and curr_candle.close > prev_candle.close):
        return False
    
    # Current body is larger (optional but preferred)
    curr_body = curr_candle.close - curr_candle.open
    prev_body = prev_candle.open - prev_candle.close
    if curr_body <= prev_body:
        return False
    
    return True
```

#### Bearish Engulfing (for SHORT entries)

**Definition:**
```
1. Previous candle (N-1) is bullish:
   - close[N-1] > open[N-1]

2. Current candle (N) is bearish:
   - close[N] < open[N]

3. Current candle completely engulfs previous candle body:
   - open[N] > open[N-1]    # Opens above or at previous open
   - close[N] < close[N-1]  # Closes below previous close

4. Current candle closes well below previous candle:
   - (open[N] - close[N]) > (close[N-1] - open[N-1])  # Current body larger
   - close[N] < open[N-1]   # Closes below previous open
```

#### Bullish Rejection (for LONG entries)

**Definition:** Previous candle with large downward wick, closed in upper half.

```
1. Previous candle is bearish or has large lower wick:
   - lower_wick = open[N-1] - low[N-1]  (or close - low if bullish)
   - body = abs(close[N-1] - open[N-1])
   - wick_to_body_ratio = lower_wick / max(body, 1)  # Avoid division by zero
   - rejection_wick_ratio >= 1.5 (configurable)

2. Previous candle closes in upper half (shows rejection):
   - close[N-1] > (open[N-1] + close[N-1]) / 2  (closes in upper 50%)

3. Current candle is bullish:
   - close[N] > open[N]

4. Current candle closes above previous candle's open:
   - close[N] > open[N-1]
```

**Pseudocode:**
```python
def is_bullish_rejection(prev_candle, curr_candle):
    # Calculate wick ratio
    lower_wick = prev_candle.open - prev_candle.low
    if lower_wick <= 0:
        return False
    
    body = abs(prev_candle.close - prev_candle.open)
    wick_ratio = lower_wick / max(body, 0.0001)
    
    if wick_ratio < 1.5:  # configurable
        return False
    
    # Previous closes in upper half
    midpoint = (prev_candle.open + prev_candle.close) / 2
    if prev_candle.close <= midpoint:
        return False
    
    # Current is bullish and closes above previous open
    if not (curr_candle.close > curr_candle.open):
        return False
    
    if curr_candle.close <= prev_candle.open:
        return False
    
    return True
```

#### Bearish Rejection (for SHORT entries)

Mirror image of bullish rejection:

```
1. Previous candle with large upward wick, closed in lower half:
   - upper_wick = high[N-1] - open[N-1]  (or high - close if bearish)
   - body = abs(close[N-1] - open[N-1])
   - wick_to_body_ratio = upper_wick / max(body, 1)
   - rejection_wick_ratio >= 1.5

2. Previous candle closes in lower half:
   - close[N-1] < (open[N-1] + close[N-1]) / 2

3. Current candle is bearish:
   - close[N] < open[N]

4. Current candle closes below previous candle's open:
   - close[N] < open[N-1]
```

### Confirmation Requirements
Either engulfing OR rejection must trigger. Both can be enabled/disabled via configuration.

**Default:** Both enabled.

### Rationale
- Engulfing patterns show reversal of momentum
- Rejection patterns show market rejecting lower/higher prices
- Deterministic mathematical definitions prevent subjectivity
- Wick ratios adapt to volatility

---

## 4. Entry Logic

### Timing
```
When:
1. A new 15M candle CLOSES
2. Trend bias is clear (LONG or SHORT from 1H filter)
3. Pullback has been detected
4. Confirmation pattern has occurred
5. All filters pass (spread, session, ATR, day-of-week, news)

Then:
  Execute market order at market open of NEXT candle
  OR immediately at market price if order is placed within same candle
```

### Anti-Duplicate Protection

Track setup state to prevent multiple entries:

```python
class SetupState:
    symbol: str
    timeframe: str  # "15m"
    candle_time: datetime  # UTC time of confirming candle
    entry_executed: bool
    entry_price: float
    entry_time: datetime
```

**Rule:**
- Once entry is executed for a setup, do not enter again from the same candle
- After position closes, apply `cooldown_minutes` before allowing new entries
- Persist state to disk to survive bot restarts

### One Position Per Symbol
```python
if len(open_positions_for_symbol) >= 1:
    reject_new_entry("Position already open for this symbol")
```

---

## 5. Stop Loss Placement

### LONG Trades

**Rule:**
Place stop loss below the most recent swing low.

```python
def calculate_long_stop_loss():
    # Find swing low: lowest low in last N candles
    # where N = swing_lookback (default: 5)
    
    swing_low = min([candle.low for candle in last_n_candles(5)])
    
    # Optional: Add ATR buffer
    atr_value = calculate_atr(14)
    atr_buffer = atr_value * atr_sl_buffer  # default: 0
    
    stop_loss = swing_low - atr_buffer
    
    # Validate distance
    sl_distance_pips = (entry_price - stop_loss) / pip_value
    
    if sl_distance_pips < min_sl_pips:
        reject_trade(f"SL distance {sl_distance_pips} < minimum {min_sl_pips}")
        return None
    
    if sl_distance_pips > max_sl_pips:
        reject_trade(f"SL distance {sl_distance_pips} > maximum {max_sl_pips}")
        return None
    
    return stop_loss
```

**Rationale:**
- Swing low is a natural support level
- Breaching it invalidates the trade setup
- ATR buffer (optional) provides safety margin
- Min/max constraints prevent unrealistic positions

### SHORT Trades

**Rule:**
Place stop loss above the most recent swing high.

```python
def calculate_short_stop_loss():
    # Find swing high: highest high in last N candles
    swing_high = max([candle.high for candle in last_n_candles(5)])
    
    # Optional: Add ATR buffer
    atr_value = calculate_atr(14)
    atr_buffer = atr_value * atr_sl_buffer
    
    stop_loss = swing_high + atr_buffer
    
    # Validate distance
    sl_distance_pips = (stop_loss - entry_price) / pip_value
    
    if sl_distance_pips < min_sl_pips:
        reject_trade(f"SL distance {sl_distance_pips} < minimum {min_sl_pips}")
        return None
    
    if sl_distance_pips > max_sl_pips:
        reject_trade(f"SL distance {sl_distance_pips} > maximum {max_sl_pips}")
        return None
    
    return stop_loss
```

---

## 6. Take Profit Placement

### Default Rule

**Risk/Reward Ratio = 1:2**

```python
def calculate_take_profit(entry_price, stop_loss, direction):
    if direction == "LONG":
        risk_distance = entry_price - stop_loss
        reward_distance = risk_distance * risk_reward_ratio  # default: 2.0
        take_profit = entry_price + reward_distance
    
    elif direction == "SHORT":
        risk_distance = stop_loss - entry_price
        reward_distance = risk_distance * risk_reward_ratio
        take_profit = entry_price - reward_distance
    
    return take_profit
```

**Example:**
```
LONG Trade:
  Entry: 1.1000
  Stop Loss: 1.0980 (20 pips risk)
  Take Profit: 1.1040 (40 pips = 2x risk)
  Ratio: 1:2
```

### Rationale
- 1:2 ratio is a standard minimum for positive expectancy
- Lower ratios may still work with high win rates but are riskier
- We do NOT adjust TP closer to increase win rate
- The goal is expectancy, not win percentage

**Formula for Positive Expectancy:**
```
Expectancy = (Win_Rate × Avg_Win) - (Loss_Rate × Avg_Loss)

Example with 40% win rate:
  Expectancy = (0.40 × 2R) - (0.60 × 1R)
  Expectancy = 0.80R - 0.60R = +0.20R per trade
```

---

## 7. Position Sizing

### Dynamic Position Size Calculation

**Never use fixed lot sizes as primary risk mechanism.**

```python
def calculate_position_size(
    account_equity,
    risk_percent,           # default: 0.005 (0.5%)
    stop_loss_distance,     # in pips
    pip_value,              # value per pip for 1 standard lot
    contract_size,          # typical: 100,000 for standard lot
):
    """
    Calculate lot size based on account equity and risk parameters.
    
    Risk Amount = Account Equity × Risk Percent
    Lot Size = Risk Amount / (SL Distance in Pips × Pip Value per Lot)
    """
    
    # 1. Calculate maximum risk in account currency
    risk_amount = account_equity * risk_percent
    
    # 2. Calculate cost per pip per standard lot
    # For most pairs: pip_value = 10 USD for 100k lot
    # For JPY pairs: pip_value = 1000 JPY for 100k lot
    cost_per_pip = pip_value  # per standard lot
    
    # 3. Calculate total cost of SL distance
    sl_cost_per_lot = stop_loss_distance * cost_per_pip
    
    # 4. Calculate lot size
    lot_size = risk_amount / sl_cost_per_lot if sl_cost_per_lot > 0 else 0
    
    # 5. Validate against broker constraints
    min_lot_size = 0.01  # Typical minimum
    max_lot_size = 100   # Typical maximum (configurable per account)
    
    lot_size = max(min_lot_size, min(lot_size, max_lot_size))
    
    # 6. Round to broker precision (typically 0.01)
    lot_size = round(lot_size, 2)
    
    return lot_size
```

### Example Calculation

```
Account Equity: $100,000
Risk Per Trade: 0.5% = $500
Entry: EUR/USD 1.1000
Stop Loss: 1.0980 (20 pips risk)
Pip Value (EUR/USD): 10 USD per standard lot

Lot Size = $500 / (20 pips × $10/pip)
Lot Size = $500 / $200
Lot Size = 2.5 standard lots
Lot Size = 250,000 units
```

### Rationale
- Adapts position size to volatility (via SL distance)
- Larger SL = smaller position = less absolute risk
- Smaller SL = larger position = more absolute risk
- All trades risk same amount regardless of market conditions

---

## 8. Risk Management & Kill Switches

### Maximum Daily Loss
```python
if daily_realized_loss >= account_equity * max_daily_loss_pct:
    stop_trading(reason="Daily loss limit reached")
    # Log: "Stopped trading: Daily loss 2.1% >= limit 2.0%"
```

### Maximum Weekly Loss
```python
if weekly_realized_loss >= account_equity * max_weekly_loss_pct:
    stop_trading(reason="Weekly loss limit reached")
```

### Maximum Drawdown
```python
if current_drawdown >= account_equity * max_drawdown_pct:
    stop_trading(reason="Maximum drawdown reached")
    # Drawdown = (Peak_Equity - Current_Equity) / Peak_Equity
```

### Maximum Consecutive Losses
```python
if consecutive_losses >= max_consecutive_losses:
    stop_trading(reason="Max consecutive losses reached")
    # Reset counter on winning trade
```

### Additional Safety Checks

**Before Every Trade Attempt:**

```python
def pre_trade_safety_checks():
    
    # 1. Broker connection
    if not broker_connected():
        return False, "Broker connection lost"
    
    # 2. Data freshness (should not be older than 30 seconds)
    if data_age_seconds > 30:
        return False, "Market data stale"
    
    # 3. Account equity available
    try:
        equity = get_account_equity()
    except:
        return False, "Cannot retrieve account equity"
    
    # 4. Position sizing calculation succeeded
    try:
        pos_size = calculate_position_size(...)
        if pos_size <= 0:
            return False, "Invalid position size calculation"
    except:
        return False, "Position size calculation failed"
    
    # 5. Spread is valid and within limits
    spread = get_current_spread()
    if spread <= 0 or spread is None:
        return False, "Invalid spread data"
    
    if spread > max_spread_pips:
        return False, f"Spread {spread} > max {max_spread_pips}"
    
    # 6. Required indicators are valid
    if not validate_indicators():
        return False, "Invalid indicator values"
    
    # 7. Trading permissions available
    if not has_trading_permissions():
        return False, "Trading permissions unavailable"
    
    return True, "All checks passed"
```

---

## 9. Trade Filters

### Spread Filter
```python
if current_spread > max_spread_pips:
    reject_trade(f"Spread {current_spread} pips > {max_spread_pips} max")
```

### Volatility Filter (ATR)
```python
atr_current = calculate_atr(14)

if min_atr_pips > 0 and atr_current < min_atr_pips:
    reject_trade(f"ATR {atr_current} < minimum {min_atr_pips}")

if max_atr_pips > 0 and atr_current > max_atr_pips:
    reject_trade(f"ATR {atr_current} > maximum {max_atr_pips}")
```

### Session Filter
```python
def is_trading_session_active(sessions_list, current_utc_time):
    """
    Sessions defined in UTC:
    - London: 08:00 - 17:00 UTC
    - New York: 13:00 - 22:00 UTC
    - Tokyo: 21:00 - 06:00 UTC (next day)
    - Sydney: 22:00 - 07:00 UTC (next day)
    """
    hour = current_utc_time.hour
    
    if "london" in sessions_list:
        if 8 <= hour < 17:
            return True
    
    if "newyork" in sessions_list:
        if 13 <= hour < 22:
            return True
    
    if "tokyo" in sessions_list:
        if 21 <= hour or hour < 6:
            return True
    
    if "sydney" in sessions_list:
        if 22 <= hour or hour < 7:
            return True
    
    if "all" in sessions_list:
        return True
    
    return False
```

**Important:** Handle daylight-saving-time changes correctly. Use IANA timezone database (pytz) for UTC conversion.

### Day-of-Week Filter
```python
current_day = current_utc_time.strftime('%A').lower()  # monday, tuesday, etc.

if current_day not in trading_days:
    reject_trade(f"Trading not allowed on {current_day}")
```

### News Filter (Optional)
```python
# If news API is available:
if economic_event_scheduled_within_next_30min():
    reject_trade("Economic news event scheduled")

# If news API is NOT reliable:
# Fail safely - do NOT assume there is no news
if cannot_fetch_news_reliably():
    reject_trade("Cannot verify news calendar - failing safely")
```

---

## 10. Trade State Persistence

### What to Persist

```python
class PersistedTrade:
    symbol: str
    direction: str  # "LONG" or "SHORT"
    entry_time: datetime
    entry_price: float
    entry_candle_time: datetime  # Time of confirming 15M candle
    stop_loss: float
    take_profit: float
    position_size: float
    account_equity_at_entry: float
    risk_percent: float
    risk_amount: float
    status: str  # "OPEN", "CLOSED", "REJECTED"
    close_time: datetime (optional)
    close_price: float (optional)
    close_reason: str  # "TP", "SL", "MANUAL", etc.
    actual_pnl: float (optional)
    actual_r: float (optional)
```

### Duplicate Trade Prevention

```python
def attempt_entry(symbol, direction, entry_price, ...):
    
    # Check if position already open
    existing = find_position(symbol)
    if existing and existing.status == "OPEN":
        return False, "Position already open for symbol"
    
    # Check if in cooldown
    last_close = find_last_closed_trade(symbol)
    if last_close:
        time_since_close = now() - last_close.close_time
        if time_since_close < timedelta(minutes=cooldown_minutes):
            return False, f"Cooldown active ({cooldown_minutes} min)"
    
    # Check if same candle entry already attempted
    last_entry = find_last_entry(symbol)
    if last_entry and last_entry.entry_candle_time == current_candle_time:
        return False, "Entry already attempted from this candle"
    
    # All checks passed - create and save trade
    trade = create_trade(symbol, direction, entry_price, ...)
    save_to_persistence(trade)
    
    return True, trade
```

---

## 11. Trade Logging

Every trade decision must be logged with detailed context.

### Entry Log Format
```
[2024-01-15 14:35:00 UTC] EUR/USD LONG ENTRY
  1H Trend: LONG (1H close 1.0950 > 200 EMA 1.0920)
  200 EMA: 1.0920
  15M Price: 1.0935
  15M 20 EMA: 1.0932
  15M 50 EMA: 1.0938
  ATR(14): 32 pips
  Pullback Status: DETECTED (price within 0.5 ATR of 20/50 area)
  Confirmation Pattern: BULLISH_ENGULFING
  Entry Price: 1.0948
  Stop Loss: 1.0920 (28 pips)
  Take Profit: 1.0976 (28 pips risk × 2.0 ratio)
  Position Size: 3.6 standard lots
  Risk Percentage: 0.5% of $100,000 = $500
  Spread: 1.2 pips
  Reason: "Pullback to 20/50 area with bullish engulfing in long-biased market"
```

### Rejection Log Format
```
[2024-01-15 14:30:00 UTC] GBP/USD LONG SETUP REJECTED
  Reason: "Spread 2.4 pips > maximum allowed 1.5 pips"
  Additional Context:
    1H Trend: LONG
    Pullback: DETECTED
    Confirmation: BULLISH_ENGULFING
    Entry Price Would Have Been: 1.2548
    SL Would Have Been: 1.2520 (28 pips)
```

### Exit Log Format
```
[2024-01-15 16:45:00 UTC] EUR/USD LONG EXIT
  Entry Time: 2024-01-15 14:35:00
  Entry Price: 1.0948
  Exit Price: 1.0976
  Exit Reason: TAKE_PROFIT_HIT
  Duration: 2 hours 10 minutes
  Position Size: 3.6 lots
  Risk Taken: 0.5% ($500)
  Profit/Loss: +0.5% ($500)
  Profit in R: +2.0R
  Cumulative Account Equity: $100,500
```

---

## Summary Table

| Rule | Value | Configurable | Notes |
|------|-------|--------------|-------|
| Trend EMA | 200 | Yes | 1H timeframe |
| Entry EMA Fast | 20 | Yes | 15M timeframe |
| Entry EMA Slow | 50 | Yes | 15M timeframe |
| ATR Period | 14 | Yes | Volatility measure |
| Pullback Distance | 0.5 ATR | Yes | Adaptive to volatility |
| Swing Lookback | 5 | Yes | Candles for swing detection |
| Risk/Reward | 1:2 | Yes | Default ratio |
| Risk Per Trade | 0.5% | Yes | % of account equity |
| Max Spread | 1.5 pips | Yes | Skip if higher |
| Max Daily Loss | 2% | Yes | % of equity |
| Max Drawdown | 15% | Yes | % of peak equity |
| Cooldown | 60 min | Yes | After trade close |
| Min SL | 5 pips | Yes | Skip if smaller |
| Max SL | 100 pips | Yes | Skip if larger |

---

## Testing Checklist

Before deployment:
- [ ] All rules are mathematically defined and testable
- [ ] No subjective interpretation in signal generation
- [ ] Position sizing calculated correctly for multiple pairs
- [ ] Risk management kill switches tested
- [ ] Duplicate trade prevention verified
- [ ] Logging captures all required information
- [ ] All timeframe calculations use UTC and correct OHLC data
- [ ] Pullback and confirmation patterns verified with examples
- [ ] Stop loss placement validated for multiple setups
- [ ] Session filters handle DST changes
