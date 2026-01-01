#!/usr/bin/env python3
"""
Automatic monitoring module for Fluid positions
Checks monitored positions every 30 minutes and sends alerts
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List
from telegram import Bot
from fluid_client_multichain import MultiChainFluidClient
from database import Database

logger = logging.getLogger(__name__)


class PositionMonitor:
    """Monitor positions and send alerts"""
    
    def __init__(self, bot: Bot, db: Database, check_interval: int = 1800):
        """
        Initialize position monitor
        
        Args:
            bot: Telegram Bot instance
            db: Database instance
            check_interval: Check interval in seconds (default: 1800 = 30 minutes)
        """
        self.bot = bot
        self.db = db
        self.check_interval = check_interval
        self.fluid_client = MultiChainFluidClient()
        self.last_alerts = {}  # Track last alert time to avoid spam
        
    async def check_all_positions(self):
        """Check all monitored positions and send alerts if needed"""
        logger.info("Starting position check cycle...")
        
        try:
            # Get all monitored addresses
            monitored = self.db.get_all_monitored_addresses()
            
            if not monitored:
                logger.info("No monitored addresses found")
                return
            
            logger.info(f"Checking {len(monitored)} monitored address(es)")
            
            for user_id, address, alert_threshold, critical_threshold in monitored:
                try:
                    await self.check_address_positions(
                        user_id, address, alert_threshold, critical_threshold
                    )
                except Exception as e:
                    logger.error(f"Error checking address {address} for user {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in check_all_positions: {e}")
    
    async def check_address_positions(self, user_id: int, address: str, 
                                     alert_threshold: float, critical_threshold: float):
        """Check all positions for a specific address"""
        logger.info(f"Checking positions for address {address} (user {user_id})")
        
        # Get all positions for this address across all chains
        all_positions = []
        
        for chain_key in ['eth', 'base', 'arbitrum', 'polygon']:
            try:
                result = self.fluid_client.get_user_positions(address, chain_key)
                if result:
                    positions, chain_name = result
                    if positions:
                        for pos in positions:
                            pos['chain'] = chain_key
                            all_positions.append(pos)
            except Exception as e:
                logger.error(f"Error fetching positions on {chain_key}: {e}")
        
        if not all_positions:
            logger.info(f"No positions found for address {address}")
            return
        
        logger.info(f"Found {len(all_positions)} position(s) for address {address}")
        
        # Check each position
        for pos in all_positions:
            try:
                await self.check_position_health(
                    user_id, pos, alert_threshold, critical_threshold
                )
            except Exception as e:
                logger.error(f"Error checking position {pos.get('nftId')}: {e}")
    
    async def check_position_health(self, user_id: int, position: Dict, 
                                   alert_threshold: float, critical_threshold: float):
        """Check a single position and send alert if needed"""
        position_id = position['nftId']
        health_factor = position['health_factor']
        chain = position.get('chain', 'unknown')
        
        # Create alert key to track last alert time
        alert_key = f"{user_id}_{position_id}"
        
        # Determine alert level
        alert_type = None
        alert_emoji = None
        
        if health_factor < critical_threshold:
            alert_type = "CRITICAL"
            alert_emoji = "🔴"
        elif health_factor < alert_threshold:
            alert_type = "WARNING"
            alert_emoji = "🟠"
        
        if not alert_type:
            # Position is healthy, no alert needed
            return
        
        # Check if we already sent an alert recently (avoid spam)
        # Only send alert once per hour for the same position
        current_time = datetime.now().timestamp()
        last_alert_time = self.last_alerts.get(alert_key, 0)
        
        if current_time - last_alert_time < 3600:  # 1 hour cooldown
            logger.info(f"Skipping alert for position {position_id} (cooldown)")
            return
        
        # Update last alert time
        self.last_alerts[alert_key] = current_time
        
        # Record alert in database
        self.db.add_alert(
            user_id, position_id, health_factor, alert_type,
            f"Health factor: {health_factor:.6f}"
        )
        
        # Record position snapshot
        self.db.add_position_snapshot(
            position_id, position['owner'], health_factor, 
            position['ratio'], position['supply_usd'], position['borrow_usd']
        )
        
        # Send Telegram alert
        await self.send_alert(user_id, position, alert_type, alert_emoji, chain)
    
    async def send_alert(self, user_id: int, position: Dict, 
                        alert_type: str, alert_emoji: str, chain: str):
        """Send Telegram alert to user"""
        try:
            from chain_config import get_chain_name
            
            chain_name = get_chain_name(chain)
            position_id = position['nftId']
            health_factor = position['health_factor']
            ratio = position['ratio']
            liquidation_threshold = position['liquidation_threshold']
            
            # Format alert message
            message = f"""
{alert_emoji} *{alert_type} ALERT!*

📊 *Position #{position_id}*
🔗 Chain: {chain_name}
━━━━━━━━━━━━━━━━━━━━━

⚠️ *Health Factor: {health_factor:.6f}*

📈 Risk Metrics:
   Collateral Ratio: {ratio:.2f}%
   Liquidation Threshold: {liquidation_threshold:.2f}%
   
💰 Collateral: {position['supply_amount']:,.4f} {position['supply_token']}
   💵 ${position['supply_usd']:,.2f}

💳 Debt: {position['borrow_amount']:,.4f} {position['borrow_token']}
   💵 ${position['borrow_usd']:,.2f}

━━━━━━━━━━━━━━━━━━━━━
"""
            
            if alert_type == "CRITICAL":
                message += "\n🚨 *IMMEDIATE ACTION REQUIRED!*\n"
                message += "Your position is at high risk of liquidation.\n"
                message += "Consider:\n"
                message += "• Adding more collateral\n"
                message += "• Repaying some debt\n"
            elif alert_type == "WARNING":
                message += "\n⚠️ *Action Recommended*\n"
                message += "Your position is approaching liquidation risk.\n"
                message += "Monitor closely or adjust your position.\n"
            
            # Send message
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"Alert sent to user {user_id} for position {position_id}")
            
        except Exception as e:
            logger.error(f"Failed to send alert to user {user_id}: {e}")
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info(f"Starting position monitor (check interval: {self.check_interval}s)")
        
        while True:
            try:
                await self.check_all_positions()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next check
            logger.info(f"Next check in {self.check_interval} seconds")
            await asyncio.sleep(self.check_interval)


if __name__ == '__main__':
    # Test monitor
    import os
    from telegram import Bot
    
    logging.basicConfig(level=logging.INFO)
    
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8560001067:AAGN272A94m9_xCN-SLS-j_WP9mQJ4MkP6w')
    bot = Bot(token=BOT_TOKEN)
    db = Database()
    
    monitor = PositionMonitor(bot, db, check_interval=60)  # Test with 1 minute
    
    # Run monitor
    asyncio.run(monitor.start_monitoring())
