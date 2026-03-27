from dotenv import load_dotenv
import os
import requests
import json
load_dotenv()



url = requests('https://finnhub.io/stock/metric?symbol=AAPL&metric=all')
print(url.text)


#couldn't get this one to work