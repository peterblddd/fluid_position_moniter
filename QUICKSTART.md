# Quick Start Guide - Fluid Position Monitor Bot

## For Users (Using the Bot)

### 1. Find the Bot on Telegram
- Search for: `@FluidPositionMoniter` (or your bot name)
- Click "Start"

### 2. Query Your Position
Send any of these:
```
9540                                          # Query Position #9540
0x1247739ac8e238D21574D18dEAce064675546cfC  # Query wallet address
/stats                                        # View your query statistics
/chains                                       # List supported chains
```

### 3. Read the Response
The bot will show:
- Position details (collateral, debt, health factor)
- Risk gauge showing liquidation proximity
- Health status indicator
- Chain information

### 4. Understand the Risk Gauge
```
Liquidation Risk Gauge:
0%          85.8%          92%
|██████████████████░░|
Status: 🟠 HIGH RISK
```
- 🟢 SAFE: Far from liquidation
- 🟠 HIGH RISK: Close to liquidation
- 🔴 CRITICAL: Liquidation imminent

## For Developers (Deploying the Bot)

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Alchemy API keys (or other RPC provider)
- Git account (for deployment)

### Option 1: Deploy on Railway (Recommended - 5 minutes)

**Step 1: Create Railway Account**
- Go to [railway.app](https://railway.app)
- Sign up with GitHub

**Step 2: Create GitHub Repository**
```bash
git clone https://github.com/your-repo/fluid-bot.git
cd fluid-bot
```

**Step 3: Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

**Step 4: Connect Railway to GitHub**
- Create new project in Railway
- Select GitHub repository
- Railway auto-deploys

**Step 5: Set Environment Variables**
In Railway dashboard:
```
BOT_TOKEN=your_telegram_bot_token_here
```

**Done!** Bot is now running.

### Option 2: Deploy on VPS (DigitalOcean, Linode, etc.)

**Step 1: SSH into Server**
```bash
ssh root@your_server_ip
```

**Step 2: Install Dependencies**
```bash
apt-get update
apt-get install -y python3 python3-pip git
```

**Step 3: Clone Repository**
```bash
cd /opt
git clone https://github.com/your-repo/fluid-bot.git
cd fluid-bot
pip3 install -r requirements.txt
```

**Step 4: Set Environment Variable**
```bash
export BOT_TOKEN="your_telegram_bot_token"
```

**Step 5: Create Systemd Service**
```bash
sudo cp fluid-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fluid-bot
sudo systemctl start fluid-bot
```

**Step 6: Check Status**
```bash
sudo systemctl status fluid-bot
sudo journalctl -u fluid-bot -f
```

### Option 3: Run Locally (Testing)

**Step 1: Install Dependencies**
```bash
pip3 install -r requirements.txt
```

**Step 2: Set Environment Variable**
```bash
export BOT_TOKEN="your_telegram_bot_token"
```

**Step 3: Run Bot**
```bash
python3 bot.py
```

**Step 4: Test in Telegram**
- Open Telegram
- Search for your bot
- Send a test query: `9540`

## File Structure

```
fluid-bot/
├── bot.py                      # Main bot code
├── fluid_client_multichain.py  # Multi-chain data client
├── chain_config.py             # Chain configuration
├── rate_limiter.py             # Rate limiting
├── database.py                 # Database management
├── FluidVaultResolver.json     # Contract ABI
├── requirements.txt            # Python dependencies
├── Procfile                    # Railway deployment
├── fluid-bot.service           # Systemd service
├── README_PUBLIC.md            # User documentation
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── MAINTENANCE.md              # Maintenance guide
└── QUICKSTART.md              # This file
```

## Common Commands

### Check Bot Status
```bash
systemctl status fluid-bot
```

### View Logs
```bash
journalctl -u fluid-bot -f
```

### Restart Bot
```bash
systemctl restart fluid-bot
```

### Update Bot
```bash
cd /opt/fluid-bot
git pull origin main
pip3 install -r requirements.txt --upgrade
systemctl restart fluid-bot
```

### Check Database
```bash
ls -lh *.db
```

## Troubleshooting

### Bot Not Responding
1. Check if running: `systemctl status fluid-bot`
2. Check logs: `journalctl -u fluid-bot -f`
3. Restart: `systemctl restart fluid-bot`

### RPC Connection Error
1. Verify RPC URLs in `chain_config.py`
2. Check API quota on Alchemy
3. Test: `python3 -c "from web3 import Web3; print(Web3(Web3.HTTPProvider('your-rpc-url')).is_connected())"`

### Rate Limit Issues
1. Check user stats: `/stats` in Telegram
2. Each user has 10 queries per day
3. Limits reset daily

## Next Steps

1. **For Users**: Start using the bot! Send `/help` for more info
2. **For Developers**: 
   - Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
   - Read [MAINTENANCE.md](MAINTENANCE.md) for ongoing maintenance
   - Read [README_PUBLIC.md](README_PUBLIC.md) for full documentation

## Support

- 📖 Read documentation files
- 🔍 Check logs for errors
- 🐛 Report bugs on GitHub
- 💬 Ask questions in issues

## Key Features

✅ Multi-chain support (ETH, BASE, ARBITRUM, PLASMA, POLYGON)
✅ Automatic chain detection
✅ Risk visualization with progress bar
✅ Health factor alerts
✅ Rate limiting (10 queries/day per user)
✅ Real-time blockchain data
✅ Easy to deploy and maintain

## License

MIT License - Feel free to modify and distribute!

---

**Ready to get started? Deploy now! 🚀**
