# Fluid Position Monitor - Public Bot Deployment Guide

## Overview

This guide explains how to deploy the public Fluid Position Monitor bot to a cloud server and maintain it.

## Recommended Deployment Options

### Option 1: Railway (Recommended - Free Tier Available)
- **Cost**: Free tier available, $5/month paid tier
- **Setup Time**: 5 minutes
- **Pros**: Easy GitHub integration, automatic deployments, built-in monitoring
- **Cons**: Limited free tier resources

### Option 2: Render
- **Cost**: Free tier available
- **Setup Time**: 5 minutes
- **Pros**: Simple deployment, free tier includes 750 hours/month
- **Cons**: Spins down after 15 minutes of inactivity

### Option 3: Heroku
- **Cost**: Paid only ($5-50/month)
- **Setup Time**: 5 minutes
- **Pros**: Reliable, good documentation
- **Cons**: No free tier anymore

### Option 4: VPS (DigitalOcean, Linode, AWS)
- **Cost**: $5-20/month
- **Setup Time**: 30 minutes
- **Pros**: Full control, always running
- **Cons**: More complex setup and maintenance

## Deployment Steps (Using Railway)

### 1. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account
3. Create new project

### 2. Connect GitHub Repository
1. Fork the repository or create a new one
2. Push all bot files to GitHub
3. Connect Railway to your GitHub repository

### 3. Set Environment Variables
In Railway dashboard:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Create Procfile
Create a file named `Procfile` in the root directory:
```
worker: python3 bot.py
```

### 5. Create requirements.txt
Ensure `requirements.txt` contains:
```
python-telegram-bot==20.3
web3==6.11.3
```

### 6. Deploy
Push to GitHub, Railway will automatically deploy.

## Deployment Steps (Using VPS)

### 1. SSH into Server
```bash
ssh root@your_server_ip
```

### 2. Install Dependencies
```bash
apt-get update
apt-get install -y python3 python3-pip git
```

### 3. Clone Repository
```bash
cd /opt
git clone https://github.com/your-repo/fluid-bot.git
cd fluid-bot
```

### 4. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Set Environment Variables
```bash
export BOT_TOKEN="your_telegram_bot_token"
```

### 6. Run with Systemd (Recommended)
Create `/etc/systemd/system/fluid-bot.service`:
```ini
[Unit]
Description=Fluid Position Monitor Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fluid-bot
Environment="BOT_TOKEN=your_telegram_bot_token"
ExecStart=/usr/bin/python3 /opt/fluid-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable fluid-bot
systemctl start fluid-bot
```

Check status:
```bash
systemctl status fluid-bot
```

View logs:
```bash
journalctl -u fluid-bot -f
```

## Maintenance & Updates

### Regular Maintenance Tasks

#### Daily
- Monitor bot logs for errors
- Check rate limiter database size
- Verify all chains are responding

#### Weekly
- Clean up old database records
- Review user statistics
- Check for any API changes

#### Monthly
- Update dependencies
- Review and optimize code
- Backup databases

### Updating the Bot

#### Step 1: Pull Latest Changes
```bash
cd /opt/fluid-bot
git pull origin main
```

#### Step 2: Update Dependencies
```bash
pip3 install -r requirements.txt --upgrade
```

#### Step 3: Restart Bot
```bash
systemctl restart fluid-bot
```

#### Step 4: Verify
```bash
systemctl status fluid-bot
journalctl -u fluid-bot -f
```

### Database Cleanup

Clean up old query records (older than 30 days):
```bash
python3 << 'EOF'
from rate_limiter import RateLimiter
limiter = RateLimiter()
deleted = limiter.cleanup_old_records(days=30)
print(f"Deleted {deleted} old records")
EOF
```

### Monitoring

#### Check Bot Status
```bash
systemctl status fluid-bot
```

#### View Recent Logs
```bash
journalctl -u fluid-bot -n 50
```

#### Monitor Database Size
```bash
ls -lh *.db
```

#### Check RPC Connectivity
```bash
python3 << 'EOF'
from fluid_client_multichain import MultiChainFluidClient
from chain_config import get_all_chains

client = MultiChainFluidClient()
for chain in get_all_chains():
    try:
        client._get_client(chain)
        print(f"✅ {chain} - OK")
    except Exception as e:
        print(f"❌ {chain} - {e}")
EOF
```

## Troubleshooting

### Bot Not Responding
1. Check if process is running: `systemctl status fluid-bot`
2. Check logs: `journalctl -u fluid-bot -f`
3. Restart: `systemctl restart fluid-bot`

### RPC Connection Errors
1. Verify RPC URLs are correct in `chain_config.py`
2. Check API quota on Alchemy
3. Test connection: `python3 test_rpc.py`

### Database Errors
1. Check database file permissions
2. Verify disk space: `df -h`
3. Backup and reset database if corrupted

### High Memory Usage
1. Check database size: `ls -lh *.db`
2. Run cleanup: `python3 -c "from rate_limiter import RateLimiter; RateLimiter().cleanup_old_records()"`
3. Restart bot: `systemctl restart fluid-bot`

## Backup Strategy

### Backup Databases
```bash
#!/bin/bash
BACKUP_DIR="/opt/fluid-bot/backups"
mkdir -p $BACKUP_DIR
cp /opt/fluid-bot/*.db $BACKUP_DIR/
tar -czf $BACKUP_DIR/backup-$(date +%Y%m%d).tar.gz $BACKUP_DIR/*.db
```

### Automated Daily Backup
Add to crontab:
```bash
0 2 * * * /opt/fluid-bot/backup.sh
```

## Scaling Considerations

### If Bot Gets Popular

1. **Rate Limiting**: Already implemented (10 queries/day per user)
2. **Database Optimization**: Add indexes for frequently queried data
3. **Caching**: Implement Redis for position data caching
4. **Load Balancing**: Run multiple bot instances with shared database
5. **RPC Optimization**: Use dedicated RPC nodes instead of Alchemy

### Database Optimization
```sql
CREATE INDEX idx_user_timestamp ON user_queries(user_id, timestamp);
CREATE INDEX idx_position_id ON position_snapshots(position_id);
```

## Security Best Practices

1. **Environment Variables**: Never commit BOT_TOKEN to repository
2. **Database Backup**: Regular encrypted backups
3. **Access Control**: Restrict SSH access with firewall rules
4. **Monitoring**: Set up alerts for bot crashes
5. **Rate Limiting**: Prevent abuse with query limits
6. **Input Validation**: Validate all user inputs

## Cost Estimation

| Platform | Monthly Cost | Notes |
|----------|-------------|-------|
| Railway | $5-10 | Includes free tier |
| Render | $0-7 | Free tier available |
| DigitalOcean | $5-20 | Cheapest VPS option |
| Heroku | $7+ | No free tier |
| AWS | $5-50+ | Pay-as-you-go |

## Support & Monitoring

### Set Up Alerts
1. Monitor bot process with systemd
2. Log errors to external service (e.g., Sentry)
3. Monitor database size
4. Track API usage

### Useful Commands
```bash
# View bot logs
journalctl -u fluid-bot -f

# Check database size
du -sh *.db

# Test RPC connection
python3 -c "from web3 import Web3; print(Web3(Web3.HTTPProvider('https://eth-mainnet.g.alchemy.com/v2/...')).eth.block_number)"

# Restart bot
systemctl restart fluid-bot

# Stop bot
systemctl stop fluid-bot

# Start bot
systemctl start fluid-bot
```

## Version Control & Updates

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create pull request and merge
```

### Deployment Workflow
1. Make changes locally
2. Test thoroughly
3. Push to GitHub
4. Platform automatically deploys
5. Monitor logs for errors

## Conclusion

The bot is now ready for production deployment. Choose your preferred hosting platform and follow the deployment steps. Regular maintenance and monitoring will ensure smooth operation.

For questions or issues, refer to the troubleshooting section or check the bot logs.
