
import asyncio
from fleet.vortex_core.core.connection import AsyncConnectionPool

class ScraperBot:
    """
    Scraper using Vortex Core.
    """
    def __init__(self):
        self.pool = AsyncConnectionPool(max_connections=50)
        
    async def run(self):
        print(f"Scraper initialized with pool size {self.pool.max_connections}")
        await self.pool.request("https://example.com")
