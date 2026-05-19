import requests
from bs4 import BeautifulSoup
import time
import random  #For human-like anti-bot bypass
import pandas as pd
from urllib.parse import urljoin  # For fixing broken relative links

#Fetch Logic
BASE_URL = "https://www.moneycontrol.com"
TARGET_URL_TEMPLATE = "https://www.moneycontrol.com/news/business/economy/page-{}/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def fetch_page_html(url):
    """Handles network requests safely, isolating connection bugs."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"  [Network Error] Failed to fetch {url}: {e}")
        return None


def parse_articles(html_content, page_num):
    """Handles HTML processing and extraction safely, isolating selector bugs."""
    extracted_articles = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    #Target container with safety fallbacks
    main_container = soup.find('ul', id='fleft') or soup.find('div', class_='leftcontainer')
    news_list = main_container.find_all('li', class_='clearfix') if main_container else soup.find_all('li', class_='clearfix')

    for item in news_list:
        try:
            headline = item.find('h2').text.strip()
            raw_link = item.find('a')['href']
            summary = item.find('p').text.strip()
            
            #Ensures links are absolute, full URLs
            absolute_link = urljoin(BASE_URL, raw_link)
            
            extracted_articles.append({
                'page': page_num,
                'headline': headline,
                'summary': summary,
                'link': absolute_link
            })
        except (AttributeError, TypeError):
            #skips non-article rows, ads, or structural anomalies
            continue
            
    return extracted_articles


def main():
    """Main execution orchestration engine."""
    all_news_data = []
    print("Running Arachnet Moneycontrol Scraper Engine...")
    
    for page in range(1, 51):
        print(f"Processing Page {page}/50...")
        url = TARGET_URL_TEMPLATE.format(page)
        
        #Step 1: Fetch
        html_text = fetch_page_html(url)
        if not html_text:
            continue  #Skip to the next page if this one dropped completely
            
        #Step 2: Parse
        page_articles = parse_articles(html_text, page)
        all_news_data.extend(page_articles)
        print(f"Collected {len(page_articles)} items")
        
        #Adaptive anti-bot bypass. Random sleep between 3.0 to 7.0 seconds.
        time.sleep(random.uniform(3.0, 7.0))

    #Step 3: Clean & Save
    if all_news_data:
        df = pd.DataFrame(all_news_data)
        
        #Data QC. Drop identical rows if an article shows up twice.
        initial_count = len(df)
        df.drop_duplicates(subset=['headline'], inplace=True)
        final_count = len(df)
        
        df.to_csv('moneycontrol_economy_clean.csv', index=False)
        print(f"\n Pipeline Complete!")
        print(f"Total Extracted: {initial_count}")
        print(f"After Filtering for Duplicates: {final_count} unique articles saved to 'moneycontrol_economy_clean.csv'")
    else:
        print("\n Pipeline completed with zero data collected. Verify site wrappers.")


if __name__ == "__main__":
    main()
    





