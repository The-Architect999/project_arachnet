'''Arachnet Development Testing Module - Modular Configurations & SQL Pipeline'''
import sqlite3
import re
import pandas as pd
from parsing_engine import ez_parse

# =====================================================================
# SITE CONFIGURATIONS
# =====================================================================

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
    "pages": 30,  # Scaled down for testing stability
    "strategy": "html_dom",
    "container_tag": "li",
    "container_class": "clearfix",
    "headline_tag": "h2",
    "anchor_position": "parent",
    "summary_tag": "p",
    "date_class": "date"
}

# Select target site configuration:
active_config = moneycontrol

# =====================================================================
# DATA PIPELINE CHANNELS (Pandas Filtering & SQL Storage)
# =====================================================================

def process_and_filter_records(records):
    """Normalizes scraped textual data to catch and drop cross-site duplicate records."""
    if not records:
        print("[Data Processing] No records received for filtering.")
        return None
        
    df = pd.DataFrame(records)
    
    # 1. Generate a standardized string column for logical matching
    # Convert to lowercase, remove punctuation/special chars, and strip extra whitespaces
    df['normalized_headline'] = (
        df['headline']
        .astype(str)
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
        .str.strip()
    )
    
    # 2. Drop duplicates based on the clean normalized signature
    initial_count = len(df)
    df.drop_duplicates(subset=['normalized_headline'], inplace=True)
    final_count = len(df)
    
    print(f"[Pandas Filter] Deduplication complete. Removed {initial_count - final_count} redundant headline matches.")
    
    # 3. Drop the utility column and any rows missing core details
    df.drop(columns=['normalized_headline'], inplace=True)
    df.dropna(subset=['headline', 'link'], inplace=True)
    
    return df


def save_to_arachnet_db(df, config, db_name="arachnet.db"):
    """Inserts processed DataFrame records straight into a local SQLite database."""
    if df is None or df.empty:
        print("[SQL Database] Storage skipped. DataFrame is empty.")
        return

    # Establish connection to your SQLite pipeline file
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    table_name = "economy_news_feed"
    
    # 1. Create target data table using explicit, clean SQL definitions
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_site TEXT NOT NULL,
            headline TEXT NOT NULL UNIQUE,
            link TEXT,
            summary TEXT,
            date_captured TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 2. Prepare structured data rows for bulk insertion
    # Mapping dataframe values into a list of plain tuples
    data_tuples = [
        (config["site_name"], row["headline"], row["link"], row["summary"])
        for _, row in df.iterrows()
    ]
    
    # 3. Execute batch insertion with conflict handling to prevent crashing on existing articles
    try:
        cursor.executemany(f"""
            INSERT OR IGNORE INTO {table_name} (source_site, headline, link, summary)
            VALUES (?, ?, ?, ?);
        """, data_tuples)
        
        conn.commit()
        print(f"[SQL Database] Transaction complete. Committed {cursor.rowcount} brand new entries to '{table_name}'.")
        
    except sqlite3.Error as e:
        print(f"[SQL Database Error] Transaction failed to commit: {e}")
        conn.rollback()
        
    finally:
        conn.close()

# =====================================================================
# MAIN RUNTIME EXECUTION Loop
# =====================================================================
if __name__ == "__main__":
    # Step 1: Ingest raw data via the scraping core
    raw_records = ez_parse(active_config)
    
    # Step 2: Pass data into the pandas filtering module
    cleaned_df = process_and_filter_records(raw_records)
    
    # Step 3: Stream unique data to SQL database file
    save_to_arachnet_db(cleaned_df, active_config)