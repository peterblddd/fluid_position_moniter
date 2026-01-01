# Fluid Protocol Telegram Bot

Real-time monitoring bot for Fluid Protocol lending positions on Telegram.

## Features

- Query lending positions by Position ID
- Query all positions for a wallet address
- Display collateral, debt, collateral ratio, and health factor
- Visual risk gauge showing proximity to liquidation
- Health status indicators (Safe/Caution/Warning/Critical)
- Alert system for positions with low health factors

## File Structure

```
fluid_bot/
├── bot.py                      # Telegram Bot main program
├── fluid_client.py             # Fluid Protocol data client
├── FluidVaultResolver.json     # VaultResolver contract ABI
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

## Configuration

### 1. Environment Variables

Set the following environment variables before running:

```bash
export BOT_TOKEN="your_telegram_bot_token"
export RPC_URL="your_ethereum_rpc_url"
```

Or modify the default values directly in `bot.py`:

```python
BOT_TOKEN = 'your_telegram_bot_token'
RPC_URL = 'your_ethereum_rpc_url'
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install python-telegram-bot web3
```

## Running the Bot

```bash
python3 bot.py
```

## Usage

Interact with the bot in Telegram:

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show help message | `/start` |
| `/help` | Show help message | `/help` |
| `/position <ID>` | Query specific position | `/position 9540` |
| `/address <address>` | Query all positions for an address | `/address 0x1247...` |
| `/monitor <address>` | Query positions with alert indicators | `/monitor 0x1247...` |

### Quick Queries

Send messages directly:

- Send a number: Query the corresponding Position ID
- Send a 0x address: Query all positions for that address

### Examples

**Query Position:**
```
9540
```

**Query Address:**
```
0x1247739ac8e238D21574D18dEAce064675546cfC
```

**Monitor with Alerts:**
```
/monitor 0x1247739ac8e238D21574D18dEAce064675546cfC
```

## Response Format

### Position Information

```
📊 Position #9540
━━━━━━━━━━━━━━━━━━━━━
👤 Owner: 0x1247...6cfC
🏦 Vault: syrupUSDC / GHO

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
0%          85.7%          92%
|████████████████░░░░|
Status: 🟠 HIGH RISK
Usage: 93.2% of liquidation threshold

🟢 SAFE
```

## Health Status Indicators

| Status | Condition | Meaning |
|--------|-----------|---------|
| 🟢 SAFE | Health Factor ≥ 1.3 | Position is healthy |
| 🟡 CAUTION | 1.1 ≤ Health Factor < 1.3 | Needs monitoring |
| 🟠 WARNING | 1.05 ≤ Health Factor < 1.1 | Close to liquidation |
| 🔴 CRITICAL | Health Factor < 1.05 | Immediate action required |

## Risk Gauge Explanation

The liquidation risk gauge shows how close your position is to liquidation:

- **0%**: Safe, far from liquidation threshold
- **50%**: Moderate risk
- **85%+**: High risk, approaching liquidation
- **100%**: Liquidation threshold reached

For Position #9540:
- Current ratio: 85.77%
- Liquidation threshold: 92%
- Usage: 93.2% of threshold
- Status: 🟠 HIGH RISK

## Technical Details

### Data Source

The bot retrieves on-chain data by calling the Fluid Protocol's VaultResolver contract:

- Contract Address: `0x394Ce45678e0019c0045194a561E2bEd0FCc6Cf0`
- Methods: `positionByNftId(uint256)` and `positionsByUser(address)`

### Calculation Formulas

**Collateral Ratio:**
```
Ratio = (Debt USD / Collateral USD) × 100%
```

**Health Factor:**
```
Health Factor = Liquidation Threshold / Ratio
```

When health factor drops below 1.0, the position becomes liquidatable.

**Liquidation Risk Usage:**
```
Usage = (Current Ratio / Liquidation Threshold) × 100%
```

## Troubleshooting

### RPC Connection Failed

Ensure your RPC URL is valid and has sufficient request quota. Recommended providers:
- Alchemy: https://www.alchemy.com/
- Infura: https://infura.io/

### Bot Not Responding

1. Check that the Bot Token is correct
2. Ensure the bot is running and has no errors
3. Check the console output for error messages
4. Make sure only one bot instance is running

### Conflict Error

If you see "Conflict: terminated by other getUpdates request", ensure only one bot instance is running at a time.

## License

MIT License
