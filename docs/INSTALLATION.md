# Installation & Setup Guide

## System Requirements

- Python 3.8 or higher
- 2GB RAM minimum
- Stable internet connection
- OANDA trading account (demo or live)

## Step 1: Clone the Repository

```bash
git clone https://github.com/ttangina269-ai/forex-trading-bot.git
cd forex-trading-bot
```

## Step 2: Create Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Get OANDA API Credentials

1. Create an account at [OANDA](https://www.oanda.com/)
2. Log in and go to **Account Settings** → **API Access**
3. Generate an API token
4. Find your **Account ID** (format: `123-456-7890123-4`)

## Step 5: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
OANDA_API_TOKEN=your_actual_token_here
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_ENVIRONMENT=practice  # For demo/paper trading
DATA_CACHE_DIR=./data/cache
LOG_DIR=./logs
STATE_DIR=./state
```

**SECURITY WARNING:** Never commit `.env` to version control. The `.gitignore` should exclude it.

## Step 6: Create Directories

```bash
mkdir -p data/cache logs state
```

## Step 7: Select Configuration

Choose a configuration file based on your needs:

### Paper Trading (Recommended for Testing)
```bash
cp config/example_configs/paper_trading.yaml config/config.yaml
```

### Conservative Mode (Tight Risk Controls)
```bash
cp config/example_configs/conservative.yaml config/config.yaml
```

### Aggressive Mode (Higher Risk Tolerance)
```bash
cp config/example_configs/aggressive.yaml config/config.yaml
```

## Step 8: Review & Customize Configuration

Edit `config/config.yaml` to adjust strategy parameters:

```yaml
mode: paper  # Keep as 'paper' for testing

trading:
  symbols:
    - EUR/USD
    - GBP/USD
    - USD/JPY
  max_positions: 1
  cooldown_minutes: 60

risk_management:
  risk_per_trade: 0.005      # 0.5% per trade
  risk_reward_ratio: 2.0     # 1:2 ratio
  max_drawdown_pct: 0.15     # 15% max drawdown

indicators:
  ema_trend: 200             # Trend filter
  ema_fast: 20               # Fast EMA
  ema_slow: 50               # Slow EMA
  atr_period: 14             # Volatility

filters:
  max_spread_pips: 1.5       # Skip if spread too wide
  trading_sessions:
    - london
    - newyork
```

For detailed configuration options, see [Configuration Reference](CONFIGURATION.md).

## Step 9: Run Unit Tests

Before running live or paper trading, verify the code:

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_indicators.py::test_ema_calculation PASSED
tests/test_indicators.py::test_atr_calculation PASSED
tests/test_signals.py::test_bullish_engulfing PASSED
tests/test_signals.py::test_bearish_rejection PASSED
tests/test_position_sizing.py::test_position_size_calculation PASSED
...

================== 25 passed in 2.34s ==================
```

## Step 10: Verify Broker Connection

Test your OANDA connection:

```bash
python src/main.py --mode verify
```

Expected output:
```
✓ OANDA Connection: SUCCESS
✓ Account ID: 123-456-7890123-4
✓ Account Type: practice (demo)
✓ Account Balance: $10,000.00
✓ Leverage: 50:1
✓ Can Trade: YES
```

## Step 11: Start Paper Trading

Once all verifications pass:

```bash
python src/main.py --mode paper
```

The bot will output:
```
2024-01-15 10:00:00 INFO: Forex Trading Bot Started (PAPER MODE)
2024-01-15 10:00:00 INFO: Trading Symbols: EUR/USD, GBP/USD, USD/JPY
2024-01-15 10:00:00 INFO: Account Equity: $10,000.00
2024-01-15 10:00:00 INFO: Risk Per Trade: 0.5% ($50.00)
2024-01-15 10:00:05 INFO: Market data loaded - waiting for signals...
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'v20'"

**Solution:**
```bash
pip install v20==20.30.0
```

### Issue: "Connection refused" to OANDA

**Check:**
1. Internet connection is active
2. `OANDA_API_TOKEN` is correct in `.env`
3. `OANDA_ENVIRONMENT` is set to `practice` (not `live`)
4. API token has not expired

### Issue: "Invalid configuration" error

**Solution:**
Validate your `config/config.yaml`:
```bash
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

Should return without errors. If it fails, check YAML syntax (spaces, indentation, etc.).

### Issue: "No data for symbol EUR/USD"

**Solution:**
- Verify symbol format matches OANDA API: `EUR_USD` (with underscore)
- The bot converts `EUR/USD` → `EUR_USD` internally
- Check OANDA account allows trading this symbol

## Next Steps

1. **Paper Trading:** Run in paper mode for at least 1-2 weeks to observe:
   - Trade frequency and win rate
   - Drawdown behavior
   - Realistic spread and slippage

2. **Backtesting:** Test strategy on historical data:
   ```bash
   python src/main.py --mode backtest --from 2023-01-01 --to 2024-01-01
   ```

3. **Configuration Tuning:** After paper trading, consider:
   - Adjusting risk per trade
   - Changing session filters
   - Modifying pullback sensitivity

4. **Live Trading:** Only after:
   - Successful paper trading (30+ trades, consistent profitability)
   - Positive out-of-sample backtesting
   - Manual review and approval
   - Starting with minimal capital

See [Paper Trading Guide](PAPER_TRADING.md) and [Live Trading Guide](LIVE_TRADING.md) for more details.

## Support

For issues:
1. Check the logs in `logs/` directory
2. Enable DEBUG logging in `config.yaml`
3. Review [Strategy Rules](STRATEGY_RULES.md) for understanding
4. Open an issue on GitHub with:
   - Error message and full traceback
   - Your OS and Python version
   - Configuration file (without API keys)
   - Recent logs
