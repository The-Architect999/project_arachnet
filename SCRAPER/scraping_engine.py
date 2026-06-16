import random                                    # for human-like anti-bot pacing delays
import time                                      # to force script execution pauses
import requests                                  # step1: basic server request
import cloudscraper                              # step2: TLS-fingerprint spoofer
from selenium import webdriver                   # step3: simulate browser
from selenium.webdriver.chrome.options import Options # Line 6: Import configuration tools to adjust Chrome's runtime behavior
import undetected_chromedriver as uc #better driver for scraping

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
# =====================================================================
# TIER 1 ENGINE HELPER
# =====================================================================
def fetch_page_html(url):
    for head in HEADERS_POOL:
        try:
            response = requests.get(url, headers=head, timeout=10) #exit if no response in 10s
            response.raise_for_status() #catch bad requests and trigger except block
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"  [Header Warning] Failed with current header profile. Trying next config... Error: {e}")
            continue
    print(f"[Network Error] All headers exhausted. Failed to fetch {url}")
    return None
# =====================================================================
# TIER 2 ENGINE HELPER
# =====================================================================
def cloud_scraper(url):
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  [CloudScraper Warning] CloudScraper Failed with Error: {e}")
        return None
# =====================================================================
# MASTER PIPELINE ENGINE
# =====================================================================
def run_scraper_engine(target_url_template, expected_pages, force_dynamic=False, min_delay = 3, max_delay = 7):
    """
    force_dynamic = True: skips step 1 (requests) and step 2 (cloudscraper)
    """
    all_html_payloads = []
    print(f"[Executing Arachnet Data Pipeline Module, dynamic = {force_dynamic}]")

    # Tracking variable to handle blocks
    is_blocked = False

    if force_dynamic:
        print("skipping STEP 1 and 2, simulating Browser")
        is_blocked = True  # Force evaluation down into Tier 3 directly

    else:
        # =====================================================================
        # TIER 1: Standard Requests Execution
        # =====================================================================
        print("[STEP 1] | Testing basic headers with requests.")
        for page in range(1, expected_pages + 1):
            url = target_url_template.format(page)
            html_text = fetch_page_html(url)
            
            if not html_text:
                print(f"[STEP 1 FAIL!] | Page {page} blocked. Escalating to CloudScraper...")
                is_blocked = True
                break  # Stop loop immediately to escalate
                
            all_html_payloads.append({'page_num': page, 'html': html_text})
            print(f"[STEP 1 SUCCESSFUL!] | cached page {page} raw HTML data.")
            time.sleep(random.uniform(min_delay, max_delay))

        # =====================================================================
        # TIER 2: CloudScraper Execution
        # =====================================================================
        if is_blocked:
            print("\n[SWITCHING ENGINES] booting CloudScraper Framework...")
            is_blocked = False  # Reset state tracking flag for this execution tier
            
            for page in range(1, expected_pages + 1):
                #CHECK: Skip pages that already have clean HTML data from Tier 1
                if any(payload['page_num'] == page for payload in all_html_payloads):
                    continue

                url = target_url_template.format(page)
                html_text = cloud_scraper(url)
                
                if not html_text:
                    print(f"[STEP 2 FAIL!] | Page {page} blocked CloudScraper. Escalating to Selenium...")
                    is_blocked = True
                    break

                all_html_payloads.append({'page_num': page, 'html': html_text})
                print(f"[STEP 2 SUCCESSFUL!] | cached page {page} raw HTML data.")
                time.sleep(random.uniform(min_delay, max_delay))

    # =====================================================================
    # TIER 3: Optimized Selenium Execution
    # =====================================================================
    if is_blocked:
        print("\n[SWITCHING ENGINES] Deploying Browser Automation...")
            
        driver = None # placeholder
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            driver = uc.Chrome(options=chrome_options)
                
            for page in range(1, expected_pages + 1):
                #CHECK: Skip pages already pulled successfully by prior engines
                if any(payload['page_num'] == page for payload in all_html_payloads):
                    #creates a list of booleans to check if page exists in all_html
                    #if page in the current loop exists in page in all_html, skip that page
                    continue

                url = target_url_template.format(page)
                print(f"Processing Page {page}/{expected_pages} via Browser Automation...")
                
                driver.get(url)
                time.sleep(5) # for wet html
                    
                html_text = driver.page_source
                    
                if not html_text or "Access Denied" in html_text:
                    print(f"[STEP 3 FAIL!] | Page {page} blocked browser instance. Out of Options!")
                    break
                        
                all_html_payloads.append({'page_num': page, 'html': html_text})
                print(f"[STEP 3 SUCCESSFUL!] | cached page {page} browser HTML source.")
                    
        except Exception as e:
            print(f"  [Selenium Critical Failure] Arachnet Pipeline failed, Error: {e}")
                
        finally:
            if driver:
                driver.quit()

    return all_html_payloads
