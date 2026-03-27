from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import sys

product = "playstation5"#sys.argv[1]
counter = 1 #rangex with for loop

driver = webdriver.Chrome()
driver.get(f"https://www.flipkart.com/search?q={product}5&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page={counter}")


element = driver.find_element(By.ID, "jsonLD")
json_text = element.get_attribute('innerHTML')
#Convert string to a Python list/dictionary
data = json.loads(json_text)

# Look for any element that contains the Rupee symbol '₹'
# Use .find_elements to get a LIST of all price tags
price_elements = list(driver.find_elements(By.CLASS_NAME, "RGLWAk"))


# 1. Wait up to 10 seconds for the product cards to actually appear
wait = WebDriverWait(driver, 10)
# We look for any div that looks like a product container (usually starts with '_1AtV' or has a test-id)
# If classes fail, we target the 'title' attribute which is much more stable
try:
    product_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, '_1AtV') or @data-id]")))
    
    for card in product_cards:
        try:
            # Locate the Name using the title attribute of the link
            name_element = card.find_element(By.XPATH, ".//a[contains(@class, 'title') or @title]")
            name = name_element.get_attribute("title")
            link = name_element.get_attribute("href")

            # Locate the PRICE by looking for the Rupee symbol
            # This is the "Nuclear Option": Find a div that contains '₹' but DOES NOT have a strikethrough (MRP)
            # Flipkart's discounted price is usually the first big price element
            price = card.find_element(By.XPATH, ".//div[contains(text(), '₹')]").text

            print(f"Name: {name}")
            print(f"Price: {price}")
            print(f"Link: {link}")
            print("-" * 30)
            
        except Exception:
            # Some divs are ads or spacing, we skip them silently
            continue

except Exception as e:
    print(f"Page took too long to load or structure changed: {e}")



# for dicts in data:
#     for lists in dicts['itemListElement']:  
#         print(f"position: {lists['position']}")
#         print(f"cost: {price_elements[int(lists['position'])].text}")
#         print(f"name: {lists['name']}")
#         print(f"link: {lists['url']}")
#         print('*' * 50)


# # list of dict[2] - list of dict 
# [1] name
# [2] position
# [3] link



# # Loop through the list to see every price found
# for index, price in enumerate(price_elements):
#     print(f"Item {index + 1}: {price.text}")