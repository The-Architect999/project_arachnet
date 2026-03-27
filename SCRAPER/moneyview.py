import requests
from bs4 import BeautifulSoup


html = requests.get("https://www.moneycontrol.com/news/business/economy/")

soup = BeautifulSoup(html.text, 'html.parser')

section = soup.find(id="mid")

section = soup.find('section', class_='mid-contener')

# Assuming 'section' is your mid-contener
news_list = section.find_all('li', class_='clearfix') # Common class for Moneycontrol news rows

for item in news_list:
    try:
        headline = item.find('h2').text.strip()
        link = item.find('a')['href']
        summary = item.find('p').text.strip()
        
        print(f"HEADLINE: {headline}")
        print(f"SUMMARY: {summary}")
        print(f"LINK: {link}")
        print("-" * 100)
    except AttributeError:
        # This skips the ads or empty rows that don't have an <h2>
        continue



