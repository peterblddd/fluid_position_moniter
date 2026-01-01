# Fluid Position Monitor - Maintenance & Update Guide

## Overview

This guide covers how to maintain, update, and troubleshoot the public Fluid Position Monitor bot.

## Maintenance Schedule

### Daily Tasks
- [ ] Check bot logs for errors
- [ ] Monitor RPC API usage
- [ ] Verify all chains are responding
- [ ] Check for any rate limit issues

### Weekly Tasks
- [ ] Review user statistics
- [ ] Check database size
- [ ] Monitor bot performance
- [ ] Review error logs

### Monthly Tasks
- [ ] Clean up old database records
- [ ] Update dependencies
- [ ] Review and optimize code
- [ ] Backup databases
- [ ] Check for API changes

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Update documentation
- [ ] Plan new features

## Monitoring

### Check Bot Status

**Using Systemd:**
```bash
systemctl status fluid-bot
```

**Using Railway:**
- Log in to Railway dashboard
- Check deployment status and logs

**Using Render:**
- Log in to Render dashboard
- Check service status

### View Logs

**Systemd:**
```bash
# Last 50 lines
journalctl -u fluid-bot -n 50

# Real-time logs
journalctl -u fluid-bot -f

# Last hour
journalctl -u fluid-bot --since "1 hour ago"

# Specific date
journalctl -u fluid-bot --since "2024-01-01" --until "2024-01-02"
```

**Railway/Render:**
- Check deployment logs in dashboard

### Monitor Database

**Check Database Size:**
```bash
ls -lh *.db
du -sh *.db
```

**Database Statistics:**
```bash
python3 << 'EOF'
import sqlite3

# Rate limit database
conn = sqlite3.connect('rate_limit.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM user_queries")
query_count = cursor.fetchone()[0]
print(f"Total queries recorded: {query_count}")

cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_queries")
unique_users = cursor.fetchone()[0]
print(f"Unique users: {unique_users}")

conn.close()
EOF
```

### Monitor RPC Usage

**Test RPC Connection:**
```bash
python3 << 'EOF'
from fluid_client_multichain import MultiChainFluidClient
from chain_config import get_all_chains

client = MultiChainFluidClient()
for chain in get_all_chains():
    try:
        c = client._get_client(chain)
        block = c['w3'].eth.block_number
        print(f"✅ {chain:10} - Block: {block}")
    except Exception as e:
        print(f"❌ {chain:10} - Error: {e}")
EOF
```

## Updates & Upgrades

### Update Code

**Step 1: Pull Latest Changes**
```bash
cd /opt/fluid-bot
git fetch origin
git pull origin main
```

**Step 2: Review Changes**
```bash
git log --oneline -5
git diff HEAD~1
```

**Step 3: Update Dependencies**
```bash
pip3 install -r requirements.txt --upgrade
```

**Step 4: Test Changes**
```bash
python3 -m pytest tests/
# or
python3 test_rpc.py
```

**Step 5: Restart Bot**
```bash
systemctl restart fluid-bot
```

**Step 6: Verify**
```bash
systemctl status fluid-bot
journalctl -u fluid-bot -f
```

### Update Configuration

**Update Chain Configuration:**
```bash
# Edit chain_config.py
nano chain_config.py

# Then restart
systemctl restart fluid-bot
```

**Update Rate Limits:**
```bash
# Edit bot.py
nano bot.py

# Change QUERIES_PER_DAY value
# Then restart
systemctl restart fluid-bot
```

## Database Maintenance

### Clean Up Old Records

**Remove records older than 30 days:**
```bash
python3 << 'EOF'
from rate_limiter import RateLimiter
limiter = RateLimiter()
deleted = limiter.cleanup_old_records(days=30)
print(f"Deleted {deleted} old records")
EOF
```

**Optimize Database:**
```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('rate_limit.db')
cursor = conn.cursor()
cursor.execute("VACUUM")
conn.commit()
conn.close()
print("Database optimized")
EOF
```

### Backup Database

**Manual Backup:**
```bash
cp rate_limit.db rate_limit.db.backup-$(date +%Y%m%d)
```

**Automated Daily Backup:**
```bash
#!/bin/bash
# /opt/fluid-bot/backup.sh

BACKUP_DIR="/opt/fluid-bot/backups"
mkdir -p $BACKUP_DIR

# Backup databases
cp /opt/fluid-bot/rate_limit.db $BACKUP_DIR/rate_limit.db.$(date +%Y%m%d)

# Keep only last 30 days
find $BACKUP_DIR -name "*.db.*" -mtime +30 -delete

echo "Backup completed at $(date)"
```

Add to crontab:
```bash
crontab -e

# Add line:
0 2 * * * /opt/fluid-bot/backup.sh
```

### Restore from Backup

```bash
# Stop bot
systemctl stop fluid-bot

# Restore database
cp rate_limit.db.backup-20240101 rate_limit.db

# Start bot
systemctl start fluid-bot
```

## Troubleshooting

### Bot Crashes

**Check Logs:**
```bash
journalctl -u fluid-bot -n 100
```

**Common Issues:**
1. **RPC Connection Failed** - Check RPC URLs and API quotas
2. **Database Locked** - Restart bot
3. **Out of Memory** - Check database size and clean up
4. **Import Error** - Verify dependencies are installed

**Restart Bot:**
```bash
systemctl restart fluid-bot
```

### High Memory Usage

**Check Memory:**
```bash
ps aux | grep bot.py
```

**Solutions:**
1. Clean up old database records
2. Restart bot
3. Check for memory leaks in logs

**Clean Up:**
```bash
python3 << 'EOF'
from rate_limiter import RateLimiter
limiter = RateLimiter()
deleted = limiter.cleanup_old_records(days=7)
print(f"Deleted {deleted} records")
EOF
```

### RPC Errors

**Test RPC Connection:**
```bash
python3 << 'EOF'
from web3 import Web3

rpc_url = "https://eth-mainnet.g.alchemy.com/v2/your-api-key"
w3 = Web3(Web3.HTTPProvider(rpc_url))
print(f"Connected: {w3.is_connected()}")
print(f"Block: {w3.eth.block_number}")
EOF
```

**Solutions:**
1. Verify API key is correct
2. Check API quota on Alchemy
3. Try different RPC provider
4. Check internet connection

### Database Corruption

**Check Database Integrity:**
```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('rate_limit.db')
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    print(f"Database check: {result}")
except Exception as e:
    print(f"Database error: {e}")
conn.close()
EOF
```

**Recover from Corruption:**
```bash
# Stop bot
systemctl stop fluid-bot

# Backup corrupted database
mv rate_limit.db rate_limit.db.corrupted

# Bot will create new database on restart
systemctl start fluid-bot
```

## Performance Optimization

### Database Optimization

**Add Indexes:**
```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('rate_limit.db')
cursor = conn.cursor()

# Create indexes for faster queries
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_user_timestamp 
    ON user_queries(user_id, timestamp)
''')

cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_timestamp 
    ON user_queries(timestamp)
''')

conn.commit()
conn.close()
print("Indexes created")
EOF
```

### Caching

**Implement Redis Caching (Optional):**
```python
# Add to fluid_client_multichain.py
import redis

class CachedFluidClient(MultiChainFluidClient):
    def __init__(self, redis_url='redis://localhost:6379'):
        super().__init__()
        self.cache = redis.from_url(redis_url)
    
    def get_position_by_id(self, position_id, chain='eth'):
        cache_key = f"position:{chain}:{position_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return json.loads(cached), chain
        
        result, chain_name = super().get_position_by_id(position_id, chain)
        if result:
            self.cache.setex(cache_key, 300, json.dumps(result))  # 5 min cache
        return result, chain_name
```

## Security Updates

### Check for Vulnerabilities

```bash
# Check for outdated packages
pip3 list --outdated

# Update all packages
pip3 install -r requirements.txt --upgrade

# Check for security vulnerabilities
pip install safety
safety check
```

### Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Regular backups**: Daily encrypted backups
3. **Access control**: Restrict SSH access
4. **Monitoring**: Set up alerts for crashes
5. **Updates**: Keep dependencies updated

## Scaling

### If Bot Gets Popular

**Monitor Metrics:**
- Query rate per minute
- Database size growth
- RPC API usage
- Memory usage

**Scaling Options:**
1. **Increase rate limits** - Adjust QUERIES_PER_DAY
2. **Database optimization** - Add indexes, clean up old data
3. **Caching** - Implement Redis for position data
4. **Load balancing** - Run multiple bot instances
5. **Dedicated RPC** - Use dedicated RPC nodes

### Load Balancing

**Run Multiple Instances:**
```bash
# Create multiple service files
/etc/systemd/system/fluid-bot-1.service
/etc/systemd/system/fluid-bot-2.service
/etc/systemd/system/fluid-bot-3.service

# Each uses same database (SQLite handles concurrent access)
# Use webhook instead of polling for better performance
```

## Logging & Monitoring

### Set Up Logging

**Configure Logging:**
```python
# In bot.py
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('bot.log', maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### External Monitoring

**Set Up Sentry for Error Tracking:**
```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project",
    traces_sample_rate=1.0
)
```

## Documentation Updates

### Keep Documentation Current

- Update README when features change
- Document all configuration options
- Keep deployment guide updated
- Document any API changes

### Version Control

```bash
# Tag releases
git tag -a v2.1.0 -m "Release version 2.1.0"
git push origin v2.1.0

# Create changelog
cat > CHANGELOG.md << 'EOF'
# Changelog

## [2.1.0] - 2024-01-15
### Added
- New feature X
- Improved Y

### Fixed
- Bug fix Z

## [2.0.0] - 2024-01-01
### Added
- Multi-chain support
- Rate limiting
- Risk visualization
EOF
```

## Support & Help

### Common Commands

```bash
# Check bot status
systemctl status fluid-bot

# View logs
journalctl -u fluid-bot -f

# Restart bot
systemctl restart fluid-bot

# Stop bot
systemctl stop fluid-bot

# Start bot
systemctl start fluid-bot

# Check database size
du -sh *.db

# Backup database
cp rate_limit.db rate_limit.db.backup-$(date +%Y%m%d)
```

### Getting Help

1. Check logs: `journalctl -u fluid-bot -f`
2. Review troubleshooting section
3. Check GitHub issues
4. Contact bot creator

## Conclusion

Regular maintenance ensures the bot runs smoothly and reliably. Follow this guide to keep your bot healthy and up-to-date!
