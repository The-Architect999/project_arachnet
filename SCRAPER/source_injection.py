import sqlite3
import json
import os

'''
use to inject source configs to db, standalone.
'''

# 1.source configurations
livemint = {
    "site_name": "livemint",
    "url_template": "https://www.livemint.com/economy/page-{}",
    "pages": 1,
    "strategy": "json_script",
    "script_type": "application/ld+json",
    "schema_type": "ItemList",
    "array_key": "itemListElement",
    "mapping": {"headline": "name", "link": "url", "summary": "description"}
}

moneycontrol = {
    "site_name": "moneycontrol",
    "url_template": "https://www.moneycontrol.com/news/business/economy/page-{}",
    "pages": 30,  
    "strategy": "html_dom",
    "container_tag": "li",
    "container_class": "clearfix",
    "headline_tag": "h2",
    "anchor_position": "parent",
    "summary_tag": "p",
    "date_class": "date"
}

configs = [livemint, moneycontrol]

def seed_database(db_path="arachnet.db"):
    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. get unique keys from all sources
    all_keys = set()
    for config in configs:
        all_keys.update(config.keys())
    
    # use site name as primary key
    all_keys.remove("site_name")
    column_definitions = ["site_name TEXT PRIMARY KEY"]
    
    #format pages as int and the rest as text
    for key in all_keys:
        if key == "pages":
            column_definitions.append(f"{key} INTEGER")
        else:
            column_definitions.append(f"{key} TEXT")
            
    # 3. Create the table matching the keys exactly
    create_table_sql = f"CREATE TABLE IF NOT EXISTS sources (\n    {',\n    '.join(column_definitions)}\n);"
    
    print("Executing table creation schema...")
    cursor.execute(create_table_sql)
    
    # 4. Process and inject the payloads
    for config in configs:
        processed_row = {}
        for key, value in config.items():
            # If a config parameter is a dictionary,convert it to a string for SQL
            if isinstance(value, dict):
                processed_row[key] = json.dumps(value)
            else:
                processed_row[key] = value
        
        # Build dynamic Named-Placeholder UPSERT statement
        columns = list(processed_row.keys())
        placeholders = [f":{col}" for col in columns]
        
        upsert_sql = f"""
            INSERT OR REPLACE INTO sources ({', '.join(columns)})
            VALUES ({', '.join(placeholders)});
        """
        
        cursor.execute(upsert_sql, processed_row)
        print(f" -> Successfully synchronized configuration for: {config['site_name']}")
        
    conn.commit()
    conn.close()
    print("\n[SUCCESS] Pipeline source configs successfully injected into 'sources' table.")

if __name__ == "__main__":
    seed_database()