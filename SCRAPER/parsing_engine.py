import json
from bs4 import BeautifulSoup
from scraping_engine import run_scraper_engine


def parse_via_json_script(soup, config):
    """Strategy for mining structured text patterns straight out of script blocks."""
    extracted_rows = []
    script_tags = soup.find_all("script", type=config["script_type"])
    
    for script in script_tags:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            
            # Verify this specific script block matches our target schema (e.g., ItemList)
            if isinstance(data, dict) and data.get("@type") == config["schema_type"]:
                articles = data.get(config["array_key"], [])
                mapping = config["mapping"]
                
                for article in articles:
                    extracted_rows.append({
                        "headline": article.get(mapping["headline"]),
                        "link": article.get(mapping["link"]),
                        "summary": article.get(mapping["summary"]),
                        "date": "Captured"
                    })
        except (json.JSONDecodeError, TypeError, AttributeError):
            continue
            
    return extracted_rows

# =====================================================================
# PARSING WITH HTML
# =====================================================================
def parse_via_html_dom(soup, config):
    """Strategy for standard visual tag tree traversal."""
    extracted_rows = []
    blocks = soup.find_all(config["container_tag"], class_=config["container_class"])
    
    for block in blocks:
        try:
            # Deep tree extraction safely insulated against missing elements
            element = block.find(config["headline_tag"])
            headline, link = None, None
            
            if element:
                # Dynamically resolve anchor location based on configuration key
                position = config.get("anchor_position", "child")
                
                if position == "child":
                    a_tag = element.find("a")
                elif position == "parent":
                    a_tag = element.find_parent("a")
                else:
                    a_tag = element if element.name == "a" else None
                
                if a_tag:
                    headline = element.get_text(strip=True)
                    link = a_tag.get("href")
            
            summary_element = block.find(config["summary_tag"])
            summary = summary_element.get_text(strip=True) if summary_element else None
            
            if headline:
                extracted_rows.append({
                    "headline": headline,
                    "link": link,
                    "summary": summary,
                    "date": "Captured"
                })
        except Exception:
            continue
            
    return extracted_rows

# =====================================================================
# MASTER PARSING CONTROLLER
# =====================================================================
# 1.Network Request (Static Tier First)
def ez_parse(active_config):
    payloads = run_scraper_engine(active_config["url_template"], expected_pages=active_config["pages"])

    final_records = []

    # 2. Route data processing based on config selection
    for item in payloads:
        page_soup = BeautifulSoup(item['html'], "html.parser")
        
        if active_config["strategy"] == "json_script":
            page_data = parse_via_json_script(page_soup, active_config)
            final_records.extend(page_data)
            
        elif active_config["strategy"] == "html_dom":
            page_data = parse_via_html_dom(page_soup, active_config)
            final_records.extend(page_data)

    # 3. If static harvesting failed completely, escalate to Browser automation
    if len(final_records) == 0:
        print("\n[Data Validation Alert] 0 records parsed. Escalating to Browser Automation Layer...")
        payloads = run_scraper_engine(active_config["url_template"], expected_pages=active_config["pages"], force_dynamic=True)
        
        for item in payloads:
            page_soup = BeautifulSoup(item['html'], "html.parser")
            if active_config["strategy"] == "json_script":
                final_records.extend(parse_via_json_script(page_soup, active_config))
            elif active_config["strategy"] == "html_dom":
                final_records.extend(parse_via_html_dom(page_soup, active_config))

    print(f"\n[Execution Summary] Total records successfully routed and saved: {len(final_records)}")
    if final_records:
        return final_records
    else:
        return []