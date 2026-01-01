#!/usr/bin/env python3
"""
Database module for storing monitored addresses and alerts
"""

import sqlite3
import logging
from typing import List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for managing monitored addresses and alerts"""
    
    def __init__(self, db_path: str = 'fluid_bot.db'):
        """Initialize database"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table for monitored addresses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitored_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    alert_threshold REAL DEFAULT 1.1,
                    critical_threshold REAL DEFAULT 1.05,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, address)
                )
            ''')
            
            # Table for alert history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    position_id INTEGER NOT NULL,
                    health_factor REAL NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table for position snapshots
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS position_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    position_id INTEGER NOT NULL,
                    owner_address TEXT NOT NULL,
                    health_factor REAL NOT NULL,
                    ratio REAL NOT NULL,
                    supply_usd REAL NOT NULL,
                    borrow_usd REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def add_monitored_address(self, user_id: int, address: str, 
                             alert_threshold: float = 1.1, 
                             critical_threshold: float = 1.05) -> bool:
        """Add an address to monitor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO monitored_addresses 
                (user_id, address, alert_threshold, critical_threshold)
                VALUES (?, ?, ?, ?)
            ''', (user_id, address.lower(), alert_threshold, critical_threshold))
            
            conn.commit()
            conn.close()
            logger.info(f"Added monitored address {address} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add monitored address: {e}")
            return False
    
    def remove_monitored_address(self, user_id: int, address: str) -> bool:
        """Remove an address from monitoring"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM monitored_addresses 
                WHERE user_id = ? AND address = ?
            ''', (user_id, address.lower()))
            
            conn.commit()
            conn.close()
            logger.info(f"Removed monitored address {address} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove monitored address: {e}")
            return False
    
    def get_monitored_addresses(self, user_id: int) -> List[Tuple]:
        """Get all monitored addresses for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, address, alert_threshold, critical_threshold 
                FROM monitored_addresses 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get monitored addresses: {e}")
            return []
    
    def get_all_monitored_addresses(self) -> List[Tuple]:
        """Get all monitored addresses across all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, address, alert_threshold, critical_threshold 
                FROM monitored_addresses
                ORDER BY created_at DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get all monitored addresses: {e}")
            return []
    
    def add_alert(self, user_id: int, position_id: int, health_factor: float, 
                  alert_type: str, message: str = None) -> bool:
        """Record an alert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_history 
                (user_id, position_id, health_factor, alert_type, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, position_id, health_factor, alert_type, message))
            
            conn.commit()
            conn.close()
            logger.info(f"Alert recorded: user={user_id}, position={position_id}, type={alert_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert: {e}")
            return False
    
    def get_recent_alerts(self, user_id: int, hours: int = 24) -> List[Tuple]:
        """Get recent alerts for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT position_id, health_factor, alert_type, message, created_at
                FROM alert_history
                WHERE user_id = ? AND created_at > datetime('now', '-' || ? || ' hours')
                ORDER BY created_at DESC
            ''', (user_id, hours))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []
    
    def add_position_snapshot(self, position_id: int, owner_address: str, 
                             health_factor: float, ratio: float, 
                             supply_usd: float, borrow_usd: float) -> bool:
        """Record a position snapshot"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO position_snapshots 
                (position_id, owner_address, health_factor, ratio, supply_usd, borrow_usd)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (position_id, owner_address.lower(), health_factor, ratio, supply_usd, borrow_usd))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add position snapshot: {e}")
            return False
    
    def get_position_history(self, position_id: int, limit: int = 100) -> List[Tuple]:
        """Get historical data for a position"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT health_factor, ratio, supply_usd, borrow_usd, created_at
                FROM position_snapshots
                WHERE position_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (position_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get position history: {e}")
            return []


if __name__ == '__main__':
    # Test database
    db = Database()
    
    # Add some test data
    db.add_monitored_address(123456, '0x1247739ac8e238D21574D18dEAce064675546cfC')
    db.add_monitored_address(123456, '0x478E169b3f828806Fb655A4ea46D40eAde7B1d61')
    
    # Get monitored addresses
    addresses = db.get_monitored_addresses(123456)
    print(f"Monitored addresses: {addresses}")
    
    # Add an alert
    db.add_alert(123456, 9540, 1.08, 'WARNING', 'Health factor below 1.1')
    
    # Get recent alerts
    alerts = db.get_recent_alerts(123456)
    print(f"Recent alerts: {alerts}")
