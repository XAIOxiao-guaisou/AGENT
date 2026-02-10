"""
Sovereign Project: CRAWLER_V1
Intent: Web Crawler Node
"""

def main():
    print("Hello from CRAWLER_V1")
    # Phase 24: Check Health
    try:
        from .vibe_check import vibe_check
        vibe_check()
    except ImportError:
        pass

if __name__ == "__main__":
    main()