import requests

# 1. The Target URL (Free API Tier)
url = "https://api.coingecko.com/api/v3/simple/price"

# 2. The Filter (Requesting specific coins in USD)
parameters = {
    'ids': 'bitcoin,ethereum,solana',
    'vs_currencies': 'usd',
    'include_24hr_change': 'true'
}

res = requests.get(url, params=parameters).json()

# 3. Processing the Intel
for coin, data in res.items():
    price = data.get('usd')
    change = data.get('usd_24h_change')
    
    #Format the output
    status = "📈" if change > 0 else "📉"
    print(f"{status} {coin.upper()}: ${price:,}")
    print(f"24h Change: {change:.2f}%")
    print("-" * 20)