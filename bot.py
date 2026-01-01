#!/usr/bin/env python3
"""
Fluid Position Monitor - Public Telegram Bot
Multi-chain support with rate limiting and automatic monitoring
Supports: ETH, BASE, ARBITRUM, PLASMA, POLYGON
"""

import os
import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from fluid_client_multichain import MultiChainFluidClient
from rate_limiter import RateLimiter
from chain_config import get_all_chains, get_chain_name
from database import Database
from monitor import PositionMonitor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8560001067:AAGN272A94m9_xCN-SLS-j_WP9mQJ4MkP6w')
QUERIES_PER_DAY = 10

# Global clients
fluid_client = None
rate_limiter = None
database = None
monitor = None


def get_fluid_client():
    """Get or create Fluid client"""
    global fluid_client
    if fluid_client is None:
        fluid_client = MultiChainFluidClient()
    return fluid_client


def get_rate_limiter():
    """Get or create rate limiter"""
    global rate_limiter
    if rate_limiter is None:
        rate_limiter = RateLimiter(queries_per_day=QUERIES_PER_DAY)
    return rate_limiter


def get_database():
    """Get or create database"""
    global database
    if database is None:
        database = Database()
    return database


def create_risk_bar(ratio: float, liquidation_threshold: float) -> str:
    """Create visual risk progress bar"""
    usage_percent = (ratio / liquidation_threshold) * 100
    bar_length = 20
    filled = int((usage_percent / 100) * bar_length)
    filled = min(filled, bar_length)
    
    bar = "█" * filled + "░" * (bar_length - filled)
    
    if usage_percent >= 95:
        risk_level = "🔴 CRITICAL"
    elif usage_percent >= 85:
        risk_level = "🟠 HIGH RISK"
    elif usage_percent >= 70:
        risk_level = "🟡 MEDIUM RISK"
    else:
        risk_level = "🟢 SAFE"
    
    bar_text = f"""
*Liquidation Risk Gauge:*
```
0%          {ratio:.1f}%          {liquidation_threshold:.0f}%
|{bar}|
```
Status: {risk_level}
Usage: {usage_percent:.1f}% of liquidation threshold
"""
    return bar_text


def get_health_status(health_factor: float) -> str:
    """Get health factor status indicator"""
    if health_factor < 1.05:
        return "🔴 CRITICAL (HF < 1.05)"
    elif health_factor < 1.15:
        return "🟠 WARNING (1.05 ≤ HF < 1.15)"
    elif health_factor < 1.25:
        return "🟡 CAUTION (1.15 ≤ HF < 1.25)"
    else:
        return "🟢 SAFE (HF ≥ 1.25)"


def format_position(pos: dict, chain_name: str = None, show_alerts: bool = False) -> str:
    """Format position information"""
    if pos['is_liquidated']:
        status = "🔴 LIQUIDATED"
    elif pos['health_factor'] < 1.05:
        status = "🔴 CRITICAL"
    elif pos['health_factor'] < 1.15:
        status = "🟠 WARNING"
    elif pos['health_factor'] < 1.25:
        status = "🟡 CAUTION"
    else:
        status = "🟢 SAFE"
    
    owner = pos['owner']
    if len(owner) > 12:
        owner_short = f"{owner[:6]}...{owner[-4:]}"
    else:
        owner_short = owner
    
    risk_bar = create_risk_bar(pos['ratio'], pos['liquidation_threshold'])
    
    alert_text = ""
    if show_alerts:
        if pos['health_factor'] < 1.05:
            alert_text = "\n⚠️ *ALERT: Health Factor Critical!*\nImmediate action required to avoid liquidation."
        elif pos['health_factor'] < 1.1:
            alert_text = "\n⚠️ *WARNING: Health Factor Low*\nConsider reducing debt or adding collateral."
    
    chain_info = f"\n🔗 Chain: {chain_name}" if chain_name else ""
    
    msg = f"""
📊 *Position #{pos['nftId']}*
━━━━━━━━━━━━━━━━━━━━━
👤 Owner: `{owner_short}`
🏦 Vault: {pos['supply_token']} / {pos['borrow_token']}{chain_info}

💰 *Collateral*
   {pos['supply_amount']:,.4f} {pos['supply_token']}
   💵 ${pos['supply_usd']:,.2f}

💳 *Debt*
   {pos['borrow_amount']:,.4f} {pos['borrow_token']}
   💵 ${pos['borrow_usd']:,.2f}

📈 *Risk Metrics*
   Collateral Ratio: {pos['ratio']:.2f}%
   Health Factor: {pos['health_factor']:.6f}
   Liquidation Threshold: {pos['liquidation_threshold']:.2f}%
   Status: {get_health_status(pos['health_factor'])}
{risk_bar}━━━━━━━━━━━━━━━━━━━━━{alert_text}
"""
    return msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_msg = """
👋 *Welcome to Fluid Position Monitor!*

I help you monitor lending positions on Fluid Protocol across multiple chains.

*Supported Chains:*
🔗 Ethereum (ETH)
🔗 Base
🔗 Arbitrum
🔗 Polygon
🔗 Plasma

*How to use:*
• Send a Position ID (e.g., `9540`)
• Send a wallet address (e.g., `0x1247...`)
• Bot will search across all chains automatically

*Commands:*
• /start - Show this message
• /help - Show help
• /stats - View your query statistics
• /chains - List supported chains
• /monitor - Monitor an address for alerts
• /unmonitor - Stop monitoring an address
• /mymonitors - View your monitored addresses

*Rate Limit:*
⏱️ You have 10 queries per day

*Examples:*
• `9540`
• `0x1247739ac8e238D21574D18dEAce064675546cfC`

*Status:*
🟢 All chains online
"""
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start(update, context)


async def chains_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supported chains"""
    chains_list = ", ".join([get_chain_name(c) for c in get_all_chains()])
    msg = f"""
*Supported Chains:*
{chains_list}

The bot automatically searches across all chains when you send a query.
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    limiter = get_rate_limiter()
    
    stats = limiter.get_user_stats(user_id)
    
    msg = f"""
📊 *Your Query Statistics*

*Today (24h):*
   Queries Used: {stats.get('queries_24h', 0)}/{QUERIES_PER_DAY}
   Remaining: {stats.get('remaining_today', QUERIES_PER_DAY)}

*This Week (7d):*
   Total Queries: {stats.get('queries_7d', 0)}

*All Time:*
   Total Queries: {stats.get('queries_total', 0)}
"""
    await update.message.reply_text(msg, parse_mode='Markdown')


async def monitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /monitor command"""
    user_id = update.effective_user.id
    
    if not context.args:
        msg = """
📡 *Monitor Address*

Usage: `/monitor <address> [alert_threshold] [critical_threshold]`

*Examples:*
• `/monitor 0x1247...6cfC`
• `/monitor 0x1247...6cfC 1.15 1.05`

*Default Thresholds:*
• Alert (🟠): HF < 1.15
• Critical (🔴): HF < 1.05

*How it works:*
1. Bot checks your positions every 30 minutes
2. Sends Telegram alert if HF drops below threshold
3. One alert per hour per position (no spam)
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    address = context.args[0]
    alert_threshold = float(context.args[1]) if len(context.args) > 1 else 1.15
    critical_threshold = float(context.args[2]) if len(context.args) > 2 else 1.05
    
    # Validate address
    if not address.startswith('0x') or len(address) != 42:
        await update.message.reply_text("❌ Invalid address format")
        return
    
    # Add to database
    db = get_database()
    success = db.add_monitored_address(user_id, address, alert_threshold, critical_threshold)
    
    if success:
        msg = f"""
✅ *Monitoring Started*

📍 Address: `{address[:10]}...{address[-8:]}`
🟠 Alert Threshold: HF < {alert_threshold}
🔴 Critical Threshold: HF < {critical_threshold}

⏱️ Checks every 30 minutes
🔔 You'll receive alerts via Telegram

Use `/mymonitors` to view all monitored addresses.
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Failed to add monitoring")


async def unmonitor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unmonitor command"""
    user_id = update.effective_user.id
    
    if not context.args:
        msg = """
🔕 *Stop Monitoring*

Usage: `/unmonitor <address>`

*Example:*
• `/unmonitor 0x1247...6cfC`

Use `/mymonitors` to see your monitored addresses.
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    address = context.args[0]
    
    # Remove from database
    db = get_database()
    success = db.remove_monitored_address(user_id, address)
    
    if success:
        msg = f"""
✅ *Monitoring Stopped*

📍 Address: `{address[:10]}...{address[-8:]}`

You will no longer receive alerts for this address.
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Address not found in your monitors")


async def mymonitors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mymonitors command"""
    user_id = update.effective_user.id
    db = get_database()
    
    monitored = db.get_monitored_addresses(user_id)
    
    if not monitored:
        msg = """
📡 *Your Monitored Addresses*

You are not monitoring any addresses yet.

Use `/monitor <address>` to start monitoring.
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    msg = "📡 *Your Monitored Addresses*\n\n"
    
    for i, (mon_id, address, alert_threshold, critical_threshold) in enumerate(monitored, 1):
        msg += f"""
{i}. `{address[:10]}...{address[-8:]}`
   🟠 Alert: HF < {alert_threshold}
   🔴 Critical: HF < {critical_threshold}

"""
    
    msg += "\nUse `/unmonitor <address>` to stop monitoring."
    
    await update.message.reply_text(msg, parse_mode='Markdown')


async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user has exceeded rate limit"""
    user_id = update.effective_user.id
    limiter = get_rate_limiter()
    
    is_allowed, used, remaining = limiter.check_rate_limit(user_id)
    
    if not is_allowed:
        msg = f"""
⏱️ *Rate Limit Exceeded*

You have used all {QUERIES_PER_DAY} queries for today.
Please try again in 24 hours.

*Your Limit Resets:*
Daily at the same time you made your first query.
"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return False
    
    if remaining <= 2:
        await update.message.reply_text(
            f"⚠️ You have {remaining} queries remaining today.",
            parse_mode='Markdown'
        )
    
    return True


async def query_position(update: Update, position_id: str):
    """Query a position across all chains"""
    try:
        if not await check_rate_limit(update, None):
            return
        
        loading_msg = await update.message.reply_text("🔍 Searching across all chains...")
        
        client = get_fluid_client()
        limiter = get_rate_limiter()
        
        results = client.search_position_across_chains(position_id)
        
        if not results:
            await loading_msg.edit_text(f"❌ Position #{position_id} not found on any chain")
            return
        
        # Record query
        limiter.record_query(update.effective_user.id, 'position', position_id)
        
        # Send results
        await loading_msg.delete()
        for pos, chain_name in results:
            msg = format_position(pos, chain_name)
            await update.message.reply_text(msg, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Failed to query position: {e}")
        await update.message.reply_text(f"❌ Query failed: {str(e)}")


async def query_address(update: Update, address: str):
    """Query address across all chains"""
    try:
        if not await check_rate_limit(update, None):
            return
        
        loading_msg = await update.message.reply_text("🔍 Searching across all chains...")
        
        client = get_fluid_client()
        limiter = get_rate_limiter()
        
        results = client.search_address_across_chains(address)
        
        if not results:
            await loading_msg.edit_text(f"❌ No positions found for this address on any chain")
            return
        
        # Record query
        limiter.record_query(update.effective_user.id, 'address', address)
        
        # Send overview
        total_positions = sum(len(positions) for positions, _ in results)
        overview = f"📋 Found {total_positions} position(s) across {len(results)} chain(s)\n\n"
        await loading_msg.edit_text(overview)
        
        # Send each position
        for positions, chain_name in results:
            for pos in positions:
                msg = format_position(pos, chain_name, show_alerts=True)
                await update.message.reply_text(msg, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Failed to query address: {e}")
        await update.message.reply_text(f"❌ Query failed: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    text = update.message.text.strip()
    
    if text.isdigit():
        await query_position(update, text)
    elif text.startswith('0x'):
        await query_address(update, text)
    else:
        await update.message.reply_text(
            "❓ Please send:\n"
            "• Position ID (e.g., `9540`)\n"
            "• Wallet address (e.g., `0x1247...`)",
            parse_mode='Markdown'
        )


async def start_monitor_task(application: Application):
    """Start the monitoring task in background"""
    global monitor
    
    bot = application.bot
    db = get_database()
    monitor = PositionMonitor(bot, db, check_interval=1800)  # 30 minutes
    
    logger.info("Starting position monitor...")
    await monitor.start_monitoring()


def main():
    """Start the bot"""
    logger.info("Starting Fluid Position Monitor Bot...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chains", chains_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("monitor", monitor_command))
    application.add_handler(CommandHandler("unmonitor", unmonitor_command))
    application.add_handler(CommandHandler("mymonitors", mymonitors_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start monitor task in background
    asyncio.create_task(start_monitor_task(application))
    
    logger.info("Bot started and waiting for messages...")
    logger.info("Position monitor will start shortly...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
