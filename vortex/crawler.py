import asyncio
import httpx
import logging
from typing import List, Set
from .storage import VortexStorage
from .parser import extract_title_and_links

logger = logging.getLogger("vortex.crawler")

class VortexCrawler:
    """
    High-performance async crawler using httpx.
    """
    def __init__(self, storage: VortexStorage, concurrency: int = 5):
        self.storage = storage
        self.semaphore = asyncio.Semaphore(concurrency)
        self.seen_urls: Set[str] = set()
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

    async def close(self):
        await self.client.aclose()

    async def crawl(self, start_urls: List[str], max_pages: int = 20):
        """Crawl pages starting from start_urls"""
        queue = asyncio.Queue()
        for url in start_urls:
            queue.put_nowait(url)
        
        count = 0
        while not queue.empty() and count < max_pages:
            url = await queue.get()
            if url in self.seen_urls:
                continue
            
            self.seen_urls.add(url)
            
            try:
                # Telemetry: Pulse check
                if count % 5 == 0:
                    logger.info(f"VORTEX STATUS: Crawled {count} pages...")

                links = await self.process_url(url)
                count += 1
                
                for link in links:
                    if link not in self.seen_urls:
                        queue.put_nowait(link)
            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
            finally:
                queue.task_done()
        
        logger.info(f"Crawl complete. Pages processed: {count}")

    async def process_url(self, url: str) -> List[str]:
        """Fetch, parse, and save a single URL"""
        async with self.semaphore:
            logger.info(f"Fetching {url}")
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    # Parse
                    html = response.text
                    title, links = extract_title_and_links(html, base_url=url)
                    
                    # Save (Persistence)
                    await self.storage.save_page(url, html, title, response.status_code)
                    
                    return links
                else:
                    logger.warning(f"Error {response.status_code} for {url}")
                    return []
            except Exception as e:
                logger.error(f"Network error for {url}: {e}")
                return []
