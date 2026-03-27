import time
from selenium import webdriver # The toolkit for browser control
from selenium.webdriver.common.by import By # The "Search Engine" for HTML elements
from selenium.webdriver.chrome.options import Options # The "Setting Menu" for Chrome

chrome_options = Options() # Create a new settings object
chrome_options.add_experimental_option("detach", True) # Toggle the "Stay Alive" switch

# Open a new Chrome window using our custom settings
driver = webdriver.Chrome(options=chrome_options) 

# Command the browser to navigate to the URL
driver.get("https://qaplayground.com/practice/input") 

# Search the page using CSS "dot" notation for classes
element = driver.find_element(By.CSS_SELECTOR, ".flex.h-9.w-full.rounded-md")

# Simulate a human typing on the keyboard into that box
element.send_keys("Gladiator")

driver.close() 
#close the browser that we had to manually keep open to observe lol

#"Headless Mode" – to explore later