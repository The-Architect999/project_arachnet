# import random
# import time
# import requests
# import cloudscraper
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service

# HEADERS_POOL = [
#     {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1'
#     },
#     {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1'
#     },
#     {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1'
#     },
#     {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1'
#     }
# ]


# def fetch_page_html(url):
#     """Iterates through headers cleanly until a request succeeds or all fail."""
#     for head in HEADERS_POOL:
#         try:
#             response = requests.get(url, headers=head, timeout=10)
#             response.raise_for_status()
#             return response.text  #Break out immediately on success
            
#         except requests.exceptions.RequestException as e:
#             # If a specific header configuration triggers an error, log it and try the next one
#             print(f"  [Header Warning] Failed with current header profile. Trying next config... Error: {e}")
#             continue
            
#     print(f"[Network Error] All headers exhausted. Failed to fetch {url}")
#     return None

# def cloud_scraper(url):
#     try:
#         scraper = cloudscraper.create_scraper()
#         response = scraper.get(url, timeout=10)
#         response.raise_for_status()
#         return response.text
        
#     except Exception as e:
#         print(f"  [CloudScraper Warning] CloudScraper Failed with Error: {e}")
#         return None

    
# def fetch_with_selenium(url):
#     """Tier 3: Launches a headless, stealth-configured browser instance.
#        Returns raw rendered HTML or None on failure."""
#     driver = None
#     try:
#         # 1. Configure browser settings to bypass detection
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  # Run invisibly in the background
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
        
#         # Tell the browser to mask its automated status
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
#         #Initialize the real automated Chrome instance
#         driver = webdriver.Chrome(options=chrome_options)
        
#         # 3. Execute the navigation
#         driver.get(url)
        
#         # Give the JavaScript/WAF handshakes a solid 5 seconds to load completely
#         time.sleep(5) 
        
#         # 4. Extract the fully executed HTML page source
#         html_source = driver.page_source
#         return html_source
        
#     except Exception as e:
#         print(f"  [Selenium Critical Failure] Arachnet Pipeline failed, Error: {e}")
#         return None
        
#     finally:
#         # CRITICAL SAFETY: Always close the browser execution process.
#         # If you forget this, background memory will fill up with dead Chrome tasks!
#         if driver:
#             driver.quit()


# def run_scraper_engine(target_url_template, expected_pages, min_delay = 3, max_delay = 7):
#     """Main execution orchestration engine. Returns compiled list of raw HTML pages."""
#     all_html_payloads = []
#     print("[Executing Arachnet Data Pipeline Module]")
#     print("[STEP 1] | Testing basic headers with requests.")
#     #break pagination if page 1 fails

#     # ----------------------------------------------------
# # TIER 1: Standard Requests
# # ----------------------------------------------------
#     for page in range(1, expected_pages + 1):
#         url = target_url_template.format(page)
#         html_text = fetch_page_html(url)
        
#         if not html_text:
#             print(f"[STEP 1 FAIL!] | Page {page} blocked. Escalating to CloudScraper...")
#             break  # Breaks out of the Requests loop entirely
            
#         all_html_payloads.append({'page_num': page, 'html': html_text})
#         time.sleep(random.uniform(min_delay, max_delay))

#     # ----------------------------------------------------
#     # TIER 2: CloudScraper (Only runs if Tier 1 didn't finish)
#     # ----------------------------------------------------
#     if len(all_html_payloads) < expected_pages:
#         print("\n[SWITCHING ENGINES] booting CloudScraper Framework...")
#         all_html_payloads.clear()  # Wipe out any partial, incomplete data
        
#         for page in range(1, expected_pages + 1):
#             url = target_url_template.format(page)
#             html_text = cloud_scraper(url)  # Make sure this helper returns a string or None
            
#             if not html_text:
#                 print(f"[STEP 2 FAIL!] | Page {page} blocked CloudScraper. Escalating to Selenium...")
#                 break  # Breaks out of the CloudScraper loop entirely
                
#             all_html_payloads.append({'page_num': page, 'html': html_text})
#             time.sleep(random.uniform(min_delay, max_delay))

#     # ----------------------------------------------------
#     # TIER 3: Selenium (Only runs if Tier 2 also failed)
#     # ----------------------------------------------------
#     if len(all_html_payloads) < expected_pages:
#         print("\n[SWITCHING ENGINES] Deploying Heavy Browser Automation...")
#         all_html_payloads.clear()
        
#         #Last resort
#         for page in range(1, expected_pages + 1):
#             url = target_url_template.format(page)
#             html_text = fetch_with_selenium(url)
            
#             if not html_text:
#                 print(f"[STEP 3 FAIL!] | Page {page} blocked. Out of Options!")
#                 break  # Breaks out of the Requests loop entirely
                
#             all_html_payloads.append({'page_num': page, 'html': html_text})
#             time.sleep(random.uniform(min_delay, max_delay))

# #selenium
# *************************************************************************************************************************
# *************************************************************************************************************************




import random                                    # for human-like anti-bot pacing delays
import time                                      # to force script execution pauses
import requests                                  # step1: basic server request
import cloudscraper                              # step2: TLS-fingerprint spoofer
from selenium import webdriver                   # step3: simulate browser
from selenium.webdriver.chrome.options import Options # Line 6: Import configuration tools to adjust Chrome's runtime behavior
import undetected_chromedriver as uc

# step1: Reqests -cycles through pool of real browser headers
HEADERS_POOL = [ 
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
]

# --- TIER 1 ENGINE HELPER ---
def fetch_page_html(url):                        
    for head in HEADERS_POOL:                    
        try:                                     
            response = requests.get(url, headers=head, timeout=10) 
            response.raise_for_status()          
            return response.text                 
        except requests.exceptions.RequestException as e: 
            print(f"  [Header Warning] Failed with current header profile. Trying next config... Error: {e}") 
            continue                             
    print(f"[Network Error] All headers exhausted. Failed to fetch {url}") 
    return None                                  

# --- TIER 2 ENGINE HELPER ---
def cloud_scraper(url):                          
    try:                                         
        scraper = cloudscraper.create_scraper()  
        response = scraper.get(url, timeout=10)  
        response.raise_for_status()               
        return response.text                     
    except Exception as e:                       
        print(f"  [CloudScraper Warning] CloudScraper Failed with Error: {e}") 
        return None                              

# --- MASTER ORCHESTRATION PIPELINE ENGINE ---
def run_scraper_engine(target_url_template, expected_pages, force_dynamic=False, min_delay = 3, max_delay = 7): 
    all_html_payloads = []                       
    print(f"[Executing Arachnet Data Pipeline Module, dynamic = {force_dynamic}]")

    # ******************************************************************  
    # TO DO:
    # if force_dynamic:
    #     print("skipping STEP 1 and 2, Moving on to Dynamic")
    # ----------------------------------------------------
    # TIER 1: Standard Requests Execution
    # ----------------------------------------------------
    # ******************************************************************

    print("[STEP 1] | Testing basic headers with requests.")
    for page in range(1, expected_pages + 1):
        url = target_url_template.format(page)
        html_text = fetch_page_html(url)
        
        if not html_text:
            print(f"[STEP 1 FAIL!] | Page {page} blocked. Escalating to CloudScraper...")
            break
            
        all_html_payloads.append({'page_num': page, 'html': html_text})
        print(f"[STEP 1 SUCCESSFUL!] | cached page {page} raw HTML data.")
        time.sleep(random.uniform(min_delay, max_delay))

    # ----------------------------------------------------
    # TIER 2: CloudScraper Execution
    # ----------------------------------------------------
    if len(all_html_payloads) < expected_pages:  #TO DO: change logic from len to bool for failed html pulls
        print("\n[SWITCHING ENGINES] booting CloudScraper Framework...") 
        all_html_payloads.clear()  #TO DO: write logic without clear and step 2/3 pick up where 1/2 left off
        
        for page in range(1, expected_pages + 1): 
            url = target_url_template.format(page)
            html_text = cloud_scraper(url)
            
            if not html_text:                    
                print(f"[STEP 2 FAIL!] | Page {page} blocked CloudScraper. Escalating to Selenium...") 
                break                            
                
            all_html_payloads.append({'page_num': page, 'html': html_text}) 
            print(f"[STEP 2 SUCCESSFUL!] | cached page {page} raw HTML data.")  
            time.sleep(random.uniform(min_delay, max_delay))  

    # ----------------------------------------------------
    # TIER 3: Optimized Selenium Execution
    # ----------------------------------------------------
    if len(all_html_payloads) < expected_pages:   
        print("\n[SWITCHING ENGINES] Deploying Heavy Browser Automation...")  
        all_html_payloads.clear()                 
        
        driver = None                             
        try:                                      
            chrome_options = Options()           
            chrome_options.add_argument("--headless") 
            chrome_options.add_argument("--no-sandbox") 
            chrome_options.add_argument("--disable-dev-shm-usage")  
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            
            driver = uc.Chrome(options=chrome_options, version_main=122)  
            
            for page in range(1, expected_pages + 1):  
                url = target_url_template.format(page)  
                print(f"Processing Page {page}/{expected_pages} via Browser Automation...")  
                
                driver.get(url)                  
                time.sleep(5)                     
                
                html_text = driver.page_source   
                
                if not html_text or "Access Denied" in html_text:  
                    print(f"[STEP 3 FAIL!] | Page {page} blocked browser instance. Out of Options!") 
                    break                        
                    
                all_html_payloads.append({'page_num': page, 'html': html_text}) 
                print(f"[STEP 3 SUCCESSFUL!] | cached page {page} browser HTML source.")  
                # NOTE:  
                
        except Exception as e:                    
            print(f"  [Selenium Critical Failure] Arachnet Pipeline failed, Error: {e}")  
            
        finally:                                  
            if driver:                            
                driver.quit()                     

    return all_html_payloads                     