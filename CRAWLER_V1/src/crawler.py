
import time
def crawl(url):
    print(f"🕷️ Crawling {url}...")
    time.sleep(0.1) # Simulate network lag
    return {"url": url, "content": "Simulated Web Data"}
