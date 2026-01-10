#!/usr/bin/env python3
"""
Keep-alive pinger for free hosting services.
Run this separately or use a free cron service like cron-job.org

Usage:
  python keep_alive.py https://your-app.railway.app
  
Or set up on cron-job.org:
  1. Go to https://cron-job.org
  2. Create free account
  3. Add job: URL = https://your-app.railway.app, every 5 minutes
"""

import sys
import time
import urllib.request

def ping(url: str):
    """Ping URL to keep service awake"""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            print(f"✓ {url} - {response.status}")
    except Exception as e:
        print(f"✗ {url} - {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python keep_alive.py <url>")
        print("Example: python keep_alive.py https://your-app.railway.app")
        sys.exit(1)
    
    url = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300  # 5 min default
    
    print(f"Pinging {url} every {interval}s")
    print("Press Ctrl+C to stop\n")
    
    while True:
        ping(url)
        time.sleep(interval)

if __name__ == "__main__":
    main()
