'''testing - make bots modular with configurations'''
import pandas as pd
from parsing_engine import ez_parse

# =====================================================================
# SITE CONFIGURATIONS (This is the only part you change for new sites)
# =====================================================================

# Layout Template A: JSON Schema Mining (Livemint Style)
livemint = {
    "url_template": "https://www.livemint.com/economy/page-{}",
    "pages": 1,
    "strategy": "json_script",
    "script_type": "application/ld+json",
    "schema_type": "ItemList",
    "array_key": "itemListElement",
    "mapping": {"headline": "name", "link": "url", "summary": "description"}
}

# Layout Template B: Standard Visual HTML DOM Drilling (Moneycontrol Style)
moneycontrol = {
    "url_template": "https://www.moneycontrol.com/news/business/economy/page-{}",
    "pages": 1,
    "strategy": "html_dom",
    "container_tag": "li",
    "container_class": "clearfix",
    "headline_tag": "h2",
    "anchor_position": "child", # "child" if <a> is inside headline, "parent" if <a> wraps around it
    "summary_tag": "p",
    "date_class": "date"
}

# Pick your active target site config here:
active_config = livemint

final_records = ez_parse(active_config)

# 4. Save Final Output
if final_records:
    df = pd.DataFrame(final_records)
    df.drop_duplicates(subset=["headline"], inplace=True)
    df.to_csv("livemint_economy_clean.csv", index=False) #todo: make modular based on site name