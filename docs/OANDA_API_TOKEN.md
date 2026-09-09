# OANDA API Token - Complete Guide

## What is an OANDA API Token?

An **OANDA API token** is a secure authentication key that allows your trading bot to:
- Connect to OANDA's trading platform
- Access real-time market data
- Place and manage trades
- Check account balance and positions
- Execute automated trading strategies

**Think of it like a password for your bot** - it proves your bot has permission to trade on your account.

---

## Types of OANDA Accounts

### Practice Account (Demo)
- ✅ Virtual money ($10,000-$1,000,000)
- ✅ Real market data and prices
- ✅ NO real money at risk
- ✅ Perfect for testing strategies
- ✅ Separate API token from live account
- ✅ **RECOMMENDED: Start here**

### Live Account
- 💰 Requires real money deposit (minimum $1,000)
- ✅ Real market data
- ⚠️ REAL MONEY AT RISK
- ⚠️ Different API token from practice
- ⚠️ Only use after 2-4 weeks of successful paper trading

---

## How to Get Your API Token

### Step 1: Create OANDA Account

1. Go to [https://www.oanda.com](https://www.oanda.com)
2. Click **"Open Account"** or **"Sign Up"**
3. Select **"Practice Account"** (NOT live)
4. Fill in your information:
   - Full name
   - Email address
   - Password (make it strong)
   - Country
   - Agree to terms
5. Click **"Create Account"**
6. Verify your email address
7. Log in to your new account

**Time: ~5 minutes**

### Step 2: Navigate to API Settings

1. Log in to your OANDA account at [myaccount.oanda.com](https://myaccount.oanda.com)
2. Click on **"Account Settings"** or **"My Account"**
3. Look for **"API Access"** or **"Developer Tools"** section
4. Click on **"Manage API Access"** or **"Create Token"**

### Step 3: Generate Your API Token

1. Click **"Generate Token"** or **"Create New Token"**
2. Give your token a name (example: `"Forex Bot v1"`)
3. Select token permissions:
   - ✅ Read account summary
   - ✅ Read account details
   - ✅ Read trades
   - ✅ Read positions
   - ✅ Create trades
   - ✅ Close trades
   - ✅ Manage trades
4. Click **"Generate"**
5. **COPY YOUR TOKEN IMMEDIATELY**
   - You'll only see it once!
   - Store it safely

**Your token will look like:**
```
pk_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```
(for practice account, starts with `pk_test_`)

### Step 4: Find Your Account ID

1. In OANDA account settings
2. Look for **"Account Details"** or **"Account Information"**
3. Find the **"Account ID"** field
4. Copy it (format: `001-001-1234567-001`)
5. **This is NOT your login username**

---

## Where to Store Your Credentials

### Create `.env` File

```bash
# In your bot directory:
cd ~/trading/forex-trading-bot

# Create .env file with your credentials:
cat > .env << EOF
OANDA_API_TOKEN=pk_test_your_actual_token_here
OANDA_ACCOUNT_ID=your_actual_account_id_here
OANDA_ENVIRONMENT=practice
DATA_CACHE_DIR=./data/cache
LOG_DIR=./logs
STATE_DIR=./state
EOF
```

Replace:
- `pk_test_your_actual_token_here` with your actual API token
- `your_actual_account_id_here` with your actual Account ID
- `practice` = demo account, `live` = real money account

### Verify .env File

```bash
# Check the file was created correctly:
cat .env

# Should show:
# OANDA_API_TOKEN=pk_test_...
# OANDA_ACCOUNT_ID=001-001-...
# OANDA_ENVIRONMENT=practice
```

---

## SECURITY - CRITICAL!

### ⚠️ Protect Your Token Like a Password

**NEVER:**
```bash
# ❌ Don't share your token
echo "My token: pk_test_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" | email to someone

# ❌ Don't commit to GitHub
git add .env
git commit -m "Add credentials"
git push  # Token is now public!

# ❌ Don't post in forums/chats
"Help! My bot won't connect. Here's my token: pk_test_..."

# ❌ Don't store in plain text files
echo "token=pk_test_..." > credentials.txt

# ❌ Don't screenshot .env
screenshot .env → share on Discord
```

**DO:**
```bash
# ✅ Store in .env file only
cat > .env << EOF
OANDA_API_TOKEN=pk_test_...
EOF

# ✅ Add .env to .gitignore
echo ".env" >> .gitignore

# ✅ Never commit .env
git status  # Should show .env is ignored

# ✅ Treat like password
# Don't share, don't screenshot, don't post online

# ✅ Rotate regularly (every 3-6 months)
# Revoke old token, generate new token, update .env
```

### If Your Token Gets Compromised

1. **Act immediately**
2. Log in to OANDA
3. Go to **API Access** settings
4. Click **"Revoke"** on the compromised token
5. Generate a **new token**
6. Update your `.env` file with new token
7. Restart your bot

---

## Test Your Credentials

### Method 1: Using Your Bot (Easiest)

```bash
# Navigate to bot directory
cd ~/trading/forex-trading-bot

# Activate virtual environment
source venv/bin/activate

# Test connection
python src/main.py --mode verify
```

**If successful, you'll see:**
```
✓ OANDA Connection: SUCCESS
✓ Account ID: 001-001-1234567-001
✓ Account Type: practice (demo)
✓ Account Balance: $10,000.00
✓ Leverage: 50:1
✓ Can Trade: YES
```

**If failed, you'll see:**
```
✗ OANDA Connection: FAILED
✗ Error: Invalid API token

Check:
1. Copy-paste token correctly (no extra spaces)
2. Copy-paste Account ID correctly
3. Verify OANDA_ENVIRONMENT setting
4. Check internet connection
```

### Method 2: Using cURL (Command Line)

```bash
# Replace YOUR_TOKEN and YOUR_ACCOUNT_ID with actual values
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api-fxpractice.oanda.com/v3/accounts/YOUR_ACCOUNT_ID
```

**If successful:**
```json
{
  "account": {
    "id": "001-001-1234567-001",
    "balance": "10000.0000",
    "currency": "USD",
    ...
  }
}
```

**If failed:**
```json
{
  "errorCode": "401",
  "errorMessage": "Unauthorized"
}
```

### Method 3: Using Python

```python
import requests
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
token = os.getenv('OANDA_API_TOKEN')
account_id = os.getenv('OANDA_ACCOUNT_ID')

# Test connection
headers = {'Authorization': f'Bearer {token}'}
url = f'https://api-fxpractice.oanda.com/v3/accounts/{account_id}'

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Connection successful!")
    print(f"Account: {data['account']['id']}")
    print(f"Balance: ${data['account']['balance']}")
else:
    print(f"✗ Connection failed: {response.status_code}")
    print(response.text)
```

---

## API Endpoints

Your bot uses different URLs depending on your environment:

### Practice Account (Demo)
```
Base URL: https://api-fxpractice.oanda.com/v3
Token format: pk_test_xxxxxxxx
Used for: Testing, learning, validation
Risk: NONE (virtual money)
```

### Live Account (Real Money)
```
Base URL: https://api-fxpractice.oanda.com/v3
Token format: pk_live_xxxxxxxx
Used for: Real trading with real money
Risk: REAL MONEY (can lose it all)
```

**Your .env file tells the bot which to use:**
```
OANDA_ENVIRONMENT=practice  # Uses practice endpoint (safe)
OANDA_ENVIRONMENT=live      # Uses live endpoint (⚠️ real money)
```

---

## Token Management

### Generate Multiple Tokens

If running multiple strategies:

```
Strategy 1 (EUR/USD):  token_eurusd
Strategy 2 (GBP/USD):  token_gbpusd
Backtesting:          token_backtest
Live Trading:         token_live (different from practice)
```

Each bot has its own `.env` file:

```bash
# Bot 1
~/bots/bot1/.env
OANDA_API_TOKEN=pk_test_token1
OANDA_ACCOUNT_ID=001-001-1111111-001

# Bot 2
~/bots/bot2/.env
OANDA_API_TOKEN=pk_test_token2
OANDA_ACCOUNT_ID=001-001-2222222-001
```

### Rotate Tokens Regularly

Every 3-6 months:

```bash
# 1. Log in to OANDA
# 2. Go to API Access settings
# 3. Revoke old token
# 4. Generate new token
# 5. Update .env file:

cat > .env << EOF
OANDA_API_TOKEN=pk_test_new_token_here
OANDA_ACCOUNT_ID=your_account_id
OANDA_ENVIRONMENT=practice
EOF

# 6. Restart bot
source venv/bin/activate
python src/main.py --mode paper
```

### Revoke Compromised Token

```bash
# 1. Log in to OANDA immediately
# 2. Go to API Access
# 3. Find the compromised token
# 4. Click "Revoke" button
# 5. Generate new token
# 6. Update .env with new token
# 7. Restart all bots

# Immediately revoke old token to prevent unauthorized access
```

---

## Common Issues

### Issue 1: "Invalid API Token"

```
Problem: Connection fails with 401 Unauthorized

Causes:
✗ Token copied incorrectly (missing characters)
✗ Token has extra spaces at beginning/end
✗ Token expired or revoked
✗ Wrong environment (practice token, live setting)

Solution:
1. Copy token again from OANDA (carefully, no extra spaces)
2. Update .env file
3. Verify token in settings: OANDA_ENVIRONMENT=practice
4. If still fails, generate new token
```

### Issue 2: "Account Not Found"

```
Problem: Connection fails with 404 Not Found

Causes:
✗ Account ID is wrong
✗ Account doesn't exist
✗ Wrong environment (practice ID with live setting)

Solution:
1. Copy Account ID from OANDA settings carefully
2. Verify format: XXX-XXX-XXXXXXX-XXX
3. Check OANDA_ENVIRONMENT matches token type
4. Verify account is active in OANDA
```

### Issue 3: "Unauthorized"

```
Problem: Connection fails with 401 Unauthorized

Causes:
✗ Token has expired
✗ Token was revoked
✗ Token permissions don't include trading

Solution:
1. Log in to OANDA
2. Check if token still exists
3. If expired/revoked, generate new token
4. Verify token has trading permissions
5. Update .env and restart
```

### Issue 4: "Network Connection Failed"

```
Problem: Bot can't reach OANDA servers

Causes:
✗ No internet connection
✗ Firewall blocking OANDA API
✗ OANDA servers down

Solution:
1. Check internet: ping google.com
2. Check firewall: sudo ufw status
3. Test OANDA status: curl https://api-fxpractice.oanda.com
4. Try again in a few moments if OANDA is down
```

---

## What Your Bot Does With API Token

Once connected, your bot automatically:

```
1. FETCH MARKET DATA
   └─ Get EUR/USD, GBP/USD, USD/JPY prices
   └─ Update every second

2. ANALYZE TRENDS
   └─ Calculate 200 EMA on 1H chart
   └─ Determine LONG/SHORT bias

3. DETECT SIGNALS
   └─ Monitor 15M pullbacks
   └─ Look for confirmation candles

4. CHECK ACCOUNT
   └─ Get current account balance
   └─ Check open positions
   └─ Calculate available margin

5. CALCULATE POSITION SIZE
   └─ Based on: Account equity, Risk %, SL distance
   └─ Example: $100,000 account, 0.5% risk, 20 pips SL = 2.5 lots

6. PLACE TRADES
   └─ Send buy/sell order to OANDA
   └─ Set stop loss
   └─ Set take profit

7. MANAGE POSITIONS
   └─ Monitor open trades
   └─ Wait for stop loss or take profit
   └─ Close trades at targets

8. TRACK RESULTS
   └─ Log all trades and results
   └─ Calculate P&L
   └─ Track win rate and expectancy
```

**All of this happens automatically with your API token!**

---

## Practice vs. Live - Key Differences

| Feature | Practice | Live |
|---------|----------|------|
| **Starting Balance** | $10,000-$1,000,000 (virtual) | $1,000+ (real money) |
| **Market Data** | Real-time | Real-time |
| **Prices** | Real | Real |
| **Risk** | None | Real money at risk |
| **Token Format** | pk_test_xxx | pk_live_xxx |
| **When to Use** | Testing, learning | After 2-4 weeks paper trading |
| **Recommendation** | **START HERE** | Only after validation |

---

## Step-by-Step Setup Checklist

- [ ] Created OANDA practice account at oanda.com
- [ ] Logged in successfully
- [ ] Found API Access section
- [ ] Generated new API token
- [ ] Copied token exactly (no extra spaces)
- [ ] Found Account ID
- [ ] Created .env file with credentials
- [ ] Added .env to .gitignore
- [ ] Tested connection: `python src/main.py --mode verify`
- [ ] Saw "✓ SUCCESS" message
- [ ] Ready to start bot!

---

## Quick Reference

```bash
# Create .env file
cat > .env << EOF
OANDA_API_TOKEN=pk_test_your_token
OANDA_ACCOUNT_ID=your_account_id
OANDA_ENVIRONMENT=practice
EOF

# Test connection
python src/main.py --mode verify

# Start bot
python src/main.py --mode paper

# View logs
tail -f logs/trading.log
```

---

## Security Checklist

- [ ] .env file is in .gitignore (never committed to GitHub)
- [ ] API token kept private (not shared, not screenshotted)
- [ ] Account password is strong and unique
- [ ] Two-factor authentication enabled on OANDA account
- [ ] API token permissions are minimal (only what's needed)
- [ ] Using practice token for testing
- [ ] Different token planned for live account (when ready)

---

## Support Resources

- **OANDA Help:** https://www.oanda.com/help/
- **OANDA API Docs:** https://developer.oanda.com/
- **OANDA Community:** https://forums.oanda.com/
- **Bot Issues:** Check logs with `tail -f logs/trading.log`

---

**Now you have everything you need to get your API token and start trading! 🚀**
