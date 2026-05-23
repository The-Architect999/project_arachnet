"""
used to generate html in the terminal to determine website config
"""

from scraping_engine import run_scraper_engine
payloads = run_scraper_engine("url_template", expected_pages="pages")

for payload in payloads:
    print(payload)