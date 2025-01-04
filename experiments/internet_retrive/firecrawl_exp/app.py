from firecrawl import FirecrawlApp
import time
import json
import os
from hashlib import md5

def get_cache_key(url, params):
    # Create a unique key based on URL and parameters
    cache_key = f"{url}_{json.dumps(params, sort_keys=True)}"
    return md5(cache_key.encode()).hexdigest()

def load_cached_result(cache_key):
    cache_file = f"cache/{cache_key}.json"
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None

def save_to_cache(cache_key, result):
    os.makedirs('cache', exist_ok=True)
    cache_file = f"cache/{cache_key}.json"
    with open(cache_file, 'w') as f:
        json.dump(result, f)

app = FirecrawlApp(api_url="http://localhost:3002/")


# Map a website:
map_result = app.map_url('https://docs.copilotkit.ai/')
map_result = app.map_url('https://docs.copilotkit.ai/guides')
print(map_result)

# Scrape a website:
# scrape_status = app.scrape_url(
#   'https://docs.copilotkit.ai/quickstart', 
#   params={'formats': ['markdown', 'html']}
# )
# print(scrape_status)

url = 'https://docs.copilotkit.ai/guides/connect-your-data#the-usecopilotreadable-hook'
params = {
    'limit': 4, 
    'scrapeOptions': {'formats': ['markdown']}
}

# Check cache first
cache_key = get_cache_key(url, params)
cached_result = load_cached_result(cache_key)

if cached_result:
    print("Loading from cache...")
    crawl_status = cached_result
else:
    print("Starting new crawl...")
    crawl_status = app.crawl_url(url, params=params, poll_interval=4)
    print("Initial crawl status:", crawl_status)

    # Add polling loop to wait for completion
    while crawl_status['status'] not in ['completed', 'failed', 'error']:
        time.sleep(4)  # Wait for 4 seconds between checks
        crawl_status = app.check_crawl_status(crawl_status['id'])
        print("Current status:", crawl_status['status'])

    # Save successful results to cache
    if crawl_status['status'] == 'completed':
        save_to_cache(cache_key, crawl_status)

print("Final crawl status:", crawl_status)
