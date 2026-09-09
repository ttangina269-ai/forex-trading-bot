# Google Cloud Deployment - Quick Checklist

Fast reference for deploying bot to Google Cloud VM.

## Prerequisites Checklist

- [ ] Google Cloud account created
- [ ] Billing enabled
- [ ] OANDA practice account created
- [ ] API token generated
- [ ] Account ID obtained
- [ ] Local machine has SSH capability (or browser)

## VM Setup (20 minutes)

```bash
# 1. Create VM via Google Cloud Console
   - Name: forex-trading-bot
   - Machine type: e2-medium
   - OS: Ubuntu 22.04 LTS
   - Boot disk: 20GB
   - Zone: us-central1-a
   - Click: Create

# 2. Connect via SSH (click "SSH" button in console)
   # Browser terminal opens automatically

# 3. Update system
sudo apt update && sudo apt upgrade -y

# 4. Install dependencies
sudo apt install python3.10 python3.10-venv python3-pip git screen -y

# 5. Verify installations
python3 --version  # Should be 3.10.x
git --version      # Should work
screen --version   # Should work
```

## Clone and Setup Bot (10 minutes)

```bash
# 1. Create trading directory
mkdir -p ~/trading && cd ~/trading

# 2. Clone repository
git clone https://github.com/ttangina269-ai/forex-trading-bot.git
cd forex-trading-bot

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
cat > .env << EOF
OANDA_API_TOKEN=your_api_token_here
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_ENVIRONMENT=practice
DATA_CACHE_DIR=./data/cache
LOG_DIR=./logs
STATE_DIR=./state
EOF

# 6. Create required directories
mkdir -p logs data/cache state

# 7. Run tests to verify
pytest tests/ -v  # Should pass 60+ tests

# 8. Test broker connection
python src/main.py --mode verify  # Should show ✓ SUCCESS
```

## Run Bot (2 minutes)

```bash
# Option A: Run in foreground (for testing)
source venv/bin/activate
python src/main.py --mode paper

# Option B: Run in background using screen (RECOMMENDED)
source venv/bin/activate
screen -S bot -d -m python src/main.py --mode paper

# List screen sessions
screen -ls

# Reattach to see output
screen -r bot

# Detach (keep bot running)
Ctrl+A, then D

# Terminate bot
screen -S bot -X quit
```

## Monitor Bot (Ongoing)

```bash
# Watch logs in real-time
tail -f logs/trading.log

# Search for entries
grep "ENTRY" logs/trading.log

# Search for exits
grep "EXIT" logs/trading.log

# Search for errors
grep "ERROR" logs/trading.log

# Count total trades
grep -c "ENTRY" logs/trading.log

# Check if bot is running
ps aux | grep "python src/main.py"

# See disk usage
du -sh logs/ data/ state/
```

## Automatic Restart on Reboot

```bash
# Create startup script
cat > ~/trading/forex-trading-bot/start_bot.sh << 'EOF'
#!/bin/bash
cd ~/trading/forex-trading-bot
source venv/bin/activate
screen -d -m -S bot python src/main.py --mode paper
echo "Bot started in screen session 'bot'"
EOF

# Make executable
chmod +x ~/trading/forex-trading-bot/start_bot.sh

# Add to crontab
crontab -e

# Add this line:
@reboot /home/USER/trading/forex-trading-bot/start_bot.sh

# (Replace USER with actual username from: whoami)

# Save and exit (Ctrl+X, Y, Enter)
```

## Troubleshooting

```bash
# Bot won't start
source venv/bin/activate
python src/main.py --mode verify  # See actual error

# Connection fails
cat .env  # Verify credentials are correct
ping google.com  # Check internet

# No trades
tail -50 logs/trading.log | grep "REJECTED"  # See why

# High CPU/memory
top  # Check resource usage (q to exit)

# Bot stuck
screen -S bot -X quit  # Kill bot
screen -S bot -d -m python src/main.py --mode paper  # Restart
```

## Cost Estimates

```
e2-medium VM (2 vCPU, 4GB RAM) running 24/7:
- Compute: ~$15-20/month
- Storage: ~$1-5/month
- Data transfer: ~$0-10/month
- Total: ~$20-35/month

To reduce:
- Use e2-small VM (1 vCPU, 2GB RAM): ~$10-15/month
- Use preemptible instances (70% cheaper, but VM can stop)
- Stop VM when not trading (weekends, etc.)
```

## Backup Logs

```bash
# Backup logs regularly
cp -r logs ~/backups/logs_$(date +%Y%m%d_%H%M%S)

# Create backup directory first
mkdir -p ~/backups

# Backup configuration
cp config/config.yaml ~/backups/config_$(date +%Y%m%d_%H%M%S).yaml
```

## SSH Connection Persistence

To keep SSH session alive when idle:

```bash
# On LOCAL machine (not VM):
cat >> ~/.ssh/config << EOF
Host *
  ServerAliveInterval 60
  ServerAliveCountMax 10
EOF
```

## Security Reminders

- [ ] .env file contains API token - NEVER commit to GitHub
- [ ] Add .env to .gitignore
- [ ] Keep API token private - don't share screenshots
- [ ] Use strong password for Google Cloud
- [ ] Enable 2FA on OANDA account
- [ ] Rotate API tokens every 3-6 months
- [ ] Monitor OANDA account for suspicious activity

## Full Deployment Timeline

```
1. Create VM:              5 minutes
2. Install dependencies:   5 minutes
3. Clone and setup bot:   10 minutes
4. Run tests and verify:   5 minutes
5. Start bot:             2 minutes
   ──────────────────────────────
   Total:                ~30 minutes

Then:
6. Paper trade:        2-4 weeks
7. Backtest:              1-2 days
8. Monitor and validate:   ongoing
9. Go live (if approved):  start with micro lots
```

## Command Reference

```bash
# SSH into VM
gcloud compute ssh forex-trading-bot --zone us-central1-a
# Or use browser SSH (easiest)

# Navigate to bot
cd ~/trading/forex-trading-bot

# Activate venv
source venv/bin/activate

# Start bot in screen
screen -S bot -d -m python src/main.py --mode paper

# View bot
screen -r bot

# Detach
Ctrl+A, D

# Watch logs
tail -f logs/trading.log

# Test connection
python src/main.py --mode verify

# Run tests
pytest tests/ -v

# Stop bot
screen -S bot -X quit

# Reboot VM (from local machine)
gcloud compute instances stop forex-trading-bot --zone us-central1-a
gcloud compute instances start forex-trading-bot --zone us-central1-a
```

## Daily Maintenance

- [ ] Check bot is running: `screen -ls`
- [ ] Review recent trades: `tail -20 logs/trading.log`
- [ ] Check for errors: `grep ERROR logs/trading.log`
- [ ] Verify disk space: `df -h`

## Weekly Maintenance

- [ ] Backup logs: `cp -r logs ~/backups/logs_$(date +%Y%m%d)`
- [ ] Review performance: `grep "EXIT" logs/trading.log`
- [ ] Check disk usage: `du -sh logs/ data/ state/`

## Monthly Maintenance

- [ ] System update: `sudo apt update && sudo apt upgrade -y`
- [ ] Rotate logs: `gzip logs/trading.log.*`
- [ ] Rotate API token (regenerate new one every 3-6 months)
- [ ] Review strategy configuration

---

**For detailed guide, see:** `docs/GOOGLE_CLOUD_DEPLOYMENT.md`
