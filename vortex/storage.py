import sqlite3
import asyncio
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime

logger = logging.getLogger("vortex.storage")

class VortexStorage:
    """
    Async wrapper for SQLite storage.
    Persists data to 'vortex_cache.db' to verify binary exclusion.
    """
    def __init__(self, db_path: str = "vortex_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema synchronously"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    url TEXT PRIMARY KEY,
                    content TEXT,
                    title TEXT,
                    status_code INTEGER,
                    timestamp DATETIME
                )
            """)
            conn.commit()
            logger.info(f"Storage initialized at {self.db_path}")

    async def save_page(self, url: str, content: str, title: str, status_code: int):
        """Save page content asynchronously"""
        def _save():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO pages (url, content, title, status_code, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (url, content, title, status_code, datetime.now()))
                conn.commit()
        
        await asyncio.to_thread(_save)
        logger.debug(f"Saved {url}")

    async def get_page(self, url: str) -> Optional[Dict]:
        """Retrieve page content asynchronously"""
        def _get():
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM pages WHERE url = ?", (url,))
                row = cursor.fetchone()
                return dict(row) if row else None
        
        return await asyncio.to_thread(_get)

    async def get_count(self) -> int:
        """Get total saved pages"""
        def _count():
            with sqlite3.connect(self.db_path) as conn:
                return conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        return await asyncio.to_thread(_count)
