"""
used to generate html in the terminal to determine website config
"""

from scraping_engine import run_scraper_engine
payloads = run_scraper_engine("https://www.moneycontrol.com/news/business/economy/page-{}", expected_pages= 1)

for payload in payloads:
    print(payload)