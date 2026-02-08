import asyncio
import logging
from pathlib import Path
from .crawler import VortexCrawler
from .storage import VortexStorage
from antigravity.utils.io_utils import safe_read

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vortex.main")

async def main():
    logger.info("🌪️ Starting Project Vortex (Async Web Scraper)...")
    
    # --- Robustness Challenge A: Dirty Config ---
    config_path = Path("vortex_config.txt")
    if config_path.exists():
        logger.info("Loading config...")
        # v1.0.1 Defense: safe_read
        config_content = safe_read(config_path)
        logger.info(f"Config content (sanitized?): {config_content!r}")
        
        if "?" in config_content or "\\ufffd" in repr(config_content):
             logger.info("✅ SUCCESS: Invalid bytes were sanitized!")
        else:
             logger.info("ℹ️ Config loaded cleanly (or bytes matched utf-8)")
    else:
        logger.warning("Config file not found!")

    # --- Robustness Challenge B: Large File Scan ---
    # We don't need to read it here, but we ensure it exists for Dashboard/Monitor to see?
    # Actually, safe_read is used inside ContextCompressor. 
    # To verify truncation, we'd need to trigger something that reads it.
    # Let's explicitly try to safe_read it here to verify logic.
    large_file = Path("vortex_large.log")
    if large_file.exists():
        logger.info(f"Attempting to read large file {large_file}...")
        large_content = safe_read(large_file)
        if "[...TRUNCATED DUE TO SIZE]" in large_content:
            logger.info("✅ SUCCESS: Large file was truncated!")
        else:
             logger.warning(f"⚠️ Large file was NOT truncated! Length: {len(large_content)}")

    # --- Execution ---
    storage = VortexStorage()
    crawler = VortexCrawler(storage)
    
    start_urls = ["https://www.example.com", "https://toscrape.com/"] # Safe targets
    
    try:
        await crawler.crawl(start_urls, max_pages=10)
    finally:
        await crawler.close()
        
    # Stats
    count = await storage.get_count()
    logger.info(f"🌪️ Vortex Mission Complete. Total pages archived: {count}")
    
    # Verify DB file existence
    db_path = Path("vortex_cache.db")
    if db_path.exists():
        logger.info(f"✅ Persistence verified: {db_path} exists ({db_path.stat().st_size} bytes)")
    else:
        logger.error("❌ Persistence failed: DB file missing!")

if __name__ == "__main__":
    asyncio.run(main())
