import re
from typing import Tuple, List, Set
from urllib.parse import urljoin, urlparse

def extract_title_and_links(html: str, base_url: str) -> Tuple[str, List[str]]:
    """
    Extract title and links from HTML content.
    Simple regex-based parser for demonstration.
    """
    # Extract Title
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "No Title"
    
    # Extract Links
    links: Set[str] = set()
    # Simple href regex
    href_matches = re.finditer(r'href=["\'](.*?)["\']', html, re.IGNORECASE)
    
    base_domain = urlparse(base_url).netloc
    
    for match in href_matches:
        link = match.group(1)
        # Normalize
        full_url = urljoin(base_url, link)
        parsed = urlparse(full_url)
        
        # Internal links only for this demo (to avoid infinite crawl of internet)
        if parsed.netloc == base_domain and parsed.scheme in ('http', 'https'):
            links.add(full_url)
            
    return title, list(links)
