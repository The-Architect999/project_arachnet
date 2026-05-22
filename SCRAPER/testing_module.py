# from scraper_module import run_scraper_engine
# from bs4 import BeautifulSoup
# # link = "https://www.moneycontrol.com/news/business/economy/page-{}/"
# link = "https://www.livemint.com/market-{}"
# payloads = run_scraper_engine(link, 3)

# # Loop through the list to unpack each page package
# for item in payloads:
#     page_number = item['page_num']
#     raw_html_string = item['html'] # Extract the actual string text
    
#     print(f"Parsing Page {page_number} content with BeautifulSoup...")
#     soup = BeautifulSoup(raw_html_string, "html.parser")
#     print(soup.text)



'''testing - make bots modular with configurations'''

# --- livemint_bot.py ---
from SCRAPER.scraping_engine import run_scraper_engine
from bs4 import BeautifulSoup

# STEP 1: Define the target configurations
# Note: make parsing engine module defined by config, 
# config will be a part of individual bot files
CONFIG = {
    "url_template": "https://www.livemint.com/economy/page-{}",
    "pages": 3,
    "container_tag": "div",
    "container_class": "headline-sec",
    "headline_tag": "h2"
}

# STEP 2: Run your universal engine to gather the raw payloads
payloads = run_scraper_engine(CONFIG["url_template"], expected_pages=CONFIG["pages"])

# STEP 3: Execute your parsing rules cleanly
all_extracted_data = []

for item in payloads:
    soup = BeautifulSoup(item['html'], "html.parser")
    
    # Isolate the main layout segments using your unique configuration parameters
    target_blocks = soup.find_all(CONFIG["container_tag"], class_=CONFIG["container_class"])
    
    for block in target_blocks:
        headline_element = block.find(CONFIG["headline_tag"])
        if headline_element:
            all_extracted_data.append(headline_element.get_text(strip=True))

print(f"Extracted {len(all_extracted_data)} unique records using site-specific blueprint rules.")





