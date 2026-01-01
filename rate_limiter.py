#!/usr/bin/env python3
"""
Rate limiter for Telegram Bot
Limits queries per user per day
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for bot queries"""
    
    def __init__(self, db_path: str = 'rate_limit.db', queries_per_day: int = 10):
        """
        Initialize rate limiter
        
        Args:
            db_path: Path to SQLite database
            queries_per_day: Maximum queries allowed per user per day
        """
        self.db_path = db_path
        self.queries_per_day = queries_per_day
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    query_type TEXT NOT NULL,
                    query_value TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                ON user_queries(user_id, timestamp)
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Rate limiter database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter database: {e}")
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Tuple of (is_allowed, queries_used, queries_remaining)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time 24 hours ago
            time_limit = datetime.now() - timedelta(hours=24)
            
            # Count queries in last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM user_queries 
                WHERE user_id = ? AND timestamp > ?
            ''', (user_id, time_limit))
            
            queries_used = cursor.fetchone()[0]
            conn.close()
            
            queries_remaining = max(0, self.queries_per_day - queries_used)
            is_allowed = queries_used < self.queries_per_day
            
            return is_allowed, queries_used, queries_remaining
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True, 0, self.queries_per_day  # Allow on error
    
    def record_query(self, user_id: int, query_type: str, query_value: str = None) -> bool:
        """
        Record a query for rate limiting
        
        Args:
            user_id: Telegram user ID
            query_type: Type of query ('position', 'address', 'monitor')
            query_value: The query value (position ID or address)
        
        Returns:
            True if recorded successfully
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_queries (user_id, query_type, query_value)
                VALUES (?, ?, ?)
            ''', (user_id, query_type, query_value))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded query for user {user_id}: {query_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record query: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get query statistics for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Last 24 hours
            time_limit_24h = datetime.now() - timedelta(hours=24)
            cursor.execute('''
                SELECT COUNT(*) FROM user_queries 
                WHERE user_id = ? AND timestamp > ?
            ''', (user_id, time_limit_24h))
            queries_24h = cursor.fetchone()[0]
            
            # Last 7 days
            time_limit_7d = datetime.now() - timedelta(days=7)
            cursor.execute('''
                SELECT COUNT(*) FROM user_queries 
                WHERE user_id = ? AND timestamp > ?
            ''', (user_id, time_limit_7d))
            queries_7d = cursor.fetchone()[0]
            
            # Total
            cursor.execute('''
                SELECT COUNT(*) FROM user_queries 
                WHERE user_id = ?
            ''', (user_id,))
            queries_total = cursor.fetchone()[0]
            
            # Query types
            cursor.execute('''
                SELECT query_type, COUNT(*) FROM user_queries 
                WHERE user_id = ? AND timestamp > ?
                GROUP BY query_type
            ''', (user_id, time_limit_24h))
            query_types = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'queries_24h': queries_24h,
                'queries_7d': queries_7d,
                'queries_total': queries_total,
                'query_types': query_types,
                'remaining_today': max(0, self.queries_per_day - queries_24h),
            }
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Clean up old query records
        
        Args:
            days: Delete records older than this many days
        
        Returns:
            Number of records deleted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM user_queries 
                WHERE timestamp < ?
            ''', (cutoff_time,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old query records")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test rate limiter
    limiter = RateLimiter(queries_per_day=10)
    
    print("Testing Rate Limiter")
    print("=" * 60)
    
    # Test user
    user_id = 123456789
    
    # Record some queries
    print(f"\nRecording 5 queries for user {user_id}...")
    for i in range(5):
        limiter.record_query(user_id, 'position', f'position_{i}')
    
    # Check rate limit
    print("\nChecking rate limit...")
    is_allowed, used, remaining = limiter.check_rate_limit(user_id)
    print(f"  Allowed: {is_allowed}")
    print(f"  Used: {used}/10")
    print(f"  Remaining: {remaining}")
    
    # Get stats
    print("\nUser statistics:")
    stats = limiter.get_user_stats(user_id)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")
