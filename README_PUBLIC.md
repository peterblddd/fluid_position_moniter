# Fluid Position Monitor - Public Bot

Real-time monitoring bot for Fluid Protocol lending positions across multiple blockchains.

## Features

✅ **Multi-Chain Support**
- Ethereum (ETH)
- Base
- Arbitrum
- Polygon
- Plasma

✅ **Automatic Chain Detection**
- Query by Position ID or wallet address
- Bot automatically searches across all chains
- Returns results from all chains where positions exist

✅ **Risk Visualization**
- Liquidation risk progress bar
- Visual health status indicators
- Real-time health factor calculation

✅ **Health Factor Alerts**
- 🟢 SAFE: Health Factor ≥ 1.3
- 🟡 CAUTION: 1.1 ≤ HF < 1.3
- 🟠 WARNING: 1.05 ≤ HF < 1.1
- 🔴 CRITICAL: HF < 1.05

✅ **Rate Limiting**
- 10 queries per user per day
- Prevents abuse and API overload
- Fair usage for all users

## Getting Started

### For Users

1. **Find the Bot on Telegram**
   - Search for: `@FluidPositionMoniter` (or your bot name)
   - Click "Start"

2. **Query Your Positions**
   - Send a Position ID: `9540`
   - Send a wallet address: `0x1247739ac8e238D21574D18dEAce064675546cfC`

3. **View Results**
   - Bot searches all chains automatically
   - Shows collateral, debt, health factor, and risk gauge
   - Displays alerts if position is at risk

### Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Show welcome message |
| `/help` | Show help message |
| `/chains` | List supported chains |
| `/stats` | View your query statistics |

### Usage Examples

**Query Position:**
```
Send: 9540

Response:
📊 Position #9540
👤 Owner: 0x1247...6cfC
🏦 Vault: syrupUSDC / GHO
🔗 Chain: Ethereum

💰 Collateral
   3,495.4938 syrupUSDC
   💵 $4,001.02

💳 Debt
   3,431.6945 GHO
   💵 $3,431.69

📈 Risk Metrics
   Collateral Ratio: 85.77%
   Health Factor: 1.072630
   Liquidation Threshold: 92.00%
   Status: 🟢 SAFE (HF ≥ 1.3)

Liquidation Risk Gauge:
0%          85.8%          92%
|██████████████████░░|
Status: 🟠 HIGH RISK
Usage: 93.2% of liquidation threshold
```

**Query Address:**
```
Send: 0x1247739ac8e238D21574D18dEAce064675546cfC

Response:
📋 Found 1 position(s) across 1 chain(s)

[Position details with alerts...]
```

## Rate Limiting

Each user has **10 queries per day**. This includes:
- Position ID queries
- Address queries
- Monitoring queries

**Check your usage:**
Send `/stats` to see:
- Queries used today
- Queries remaining
- Total queries this week

**Rate Limit Resets:**
- Daily at the same time you made your first query
- Or use `/stats` to see exact reset time

## Understanding the Risk Gauge

The liquidation risk gauge shows how close your position is to liquidation:

```
0%          Current Ratio          Liquidation Threshold
|████████████████░░|
```

- **0-70%**: 🟢 SAFE - Far from liquidation
- **70-85%**: 🟡 MEDIUM RISK - Monitor closely
- **85-95%**: 🟠 HIGH RISK - Close to liquidation
- **95%+**: 🔴 CRITICAL - Liquidation imminent

### Example: Position #9540
- Current Ratio: 85.77%
- Liquidation Threshold: 92%
- **Usage: 93.2% of threshold**
- Status: 🟠 HIGH RISK

This means the position is using 93.2% of the allowed collateral ratio before liquidation occurs.

## Health Factor Explained

**Health Factor = Liquidation Threshold / Collateral Ratio**

For Position #9540:
```
Health Factor = 92% / 85.77% = 1.0726
```

- **HF > 1.3**: Safe (🟢)
- **1.1 < HF < 1.3**: Caution (🟡)
- **1.05 < HF < 1.1**: Warning (🟠)
- **HF < 1.05**: Critical (🔴)
- **HF < 1.0**: Liquidatable

## Supported Chains

| Chain | Status | Explorer |
|-------|--------|----------|
| Ethereum | ✅ Online | etherscan.io |
| Base | ✅ Online | basescan.org |
| Arbitrum | ✅ Online | arbiscan.io |
| Polygon | ✅ Online | polygonscan.com |
| Plasma | ✅ Online | explorer.plasma.org |

The bot automatically searches all chains. No need to specify which chain!

## FAQ

### Q: How do I know which chain my position is on?
**A:** The bot shows the chain name in the response. It automatically searches all supported chains.

### Q: Can I query multiple addresses?
**A:** Yes! Each query counts toward your daily limit. Send different addresses to see positions on each.

### Q: What if I exceed my daily limit?
**A:** You'll see a message saying you've used all 10 queries. Try again tomorrow!

### Q: Is my data safe?
**A:** Yes! The bot only queries public blockchain data. No private keys or sensitive information is stored.

### Q: Why do I see different health factors on different sites?
**A:** Different protocols calculate health factors differently. This bot uses Fluid Protocol's official calculation.

### Q: Can I get alerts when my health factor drops?
**A:** Currently, you need to manually check. Future versions may include automatic alerts.

### Q: What if the bot is down?
**A:** Check the `/start` message for status. If it says "🔴 Offline", the bot is temporarily unavailable.

## Troubleshooting

### Bot Not Responding
1. Make sure you sent a valid query (Position ID or 0x address)
2. Check if you've exceeded your daily limit (`/stats`)
3. Try again in a few seconds

### "Position Not Found"
1. Verify the Position ID is correct
2. The position might be on a different chain
3. Check if the position has been liquidated

### Rate Limit Error
1. You've used all 10 queries for today
2. Check `/stats` to see when you can query again
3. Queries reset daily

### Wrong Chain
1. The bot searches all chains automatically
2. If a position is found, the chain is shown in the response
3. No action needed - the bot handles it!

## Privacy & Security

- **No Data Storage**: Only queries are logged for rate limiting
- **Public Data Only**: All data comes from public blockchains
- **No Private Keys**: The bot never asks for or stores private keys
- **Rate Limiting**: Prevents abuse and API overload

## Feedback & Support

Found a bug? Have a suggestion? 
- Report issues on GitHub
- Send feedback to the bot creator

## Technical Details

### Data Source
- On-chain data from Fluid Protocol's VaultResolver contract
- Real-time blockchain queries
- Multi-chain RPC endpoints via Alchemy

### Calculation Methods

**Collateral Ratio:**
```
Ratio = (Debt USD / Collateral USD) × 100%
```

**Health Factor:**
```
Health Factor = Liquidation Threshold / Ratio
```

**Liquidation Risk Usage:**
```
Usage = (Current Ratio / Liquidation Threshold) × 100%
```

## Version History

### v2.0 (Current)
- ✅ Multi-chain support (ETH, BASE, ARBITRUM, PLASMA, POLYGON)
- ✅ Automatic chain detection
- ✅ Risk visualization with progress bar
- ✅ Health factor alerts
- ✅ Rate limiting (10 queries/day)
- ✅ English language support
- ✅ User statistics

### v1.0
- Basic position queries
- Single chain (Ethereum only)
- Chinese language

## License

MIT License - Feel free to fork and modify!

## Disclaimer

This bot provides information only and is not financial advice. Always do your own research before making financial decisions. The creators are not responsible for any losses incurred through the use of this bot.

---

**Happy monitoring! 🚀**

For more information, visit [Fluid Protocol Docs](https://docs.fluid.instadapp.io)
