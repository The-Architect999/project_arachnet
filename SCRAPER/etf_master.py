'''Arachnet Development Testing Module - Modular Configurations & SQL Pipeline'''
import sqlite3
import re
import pandas as pd
from parsing_engine import ez_parse
import json

# =====================================================================
# FETCH ALL CONFIGS FROM DB
# =====================================================================
def fetch_all_configs(db_path="arachnet.db"):
    """
    Queries the 'sources' table for all available target sites,
    cleanses individual dataset layouts by removing NULL values,
    decodes nested JSON properties, and returns an iterable list of configurations.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1.Grab every single source configuration row in the table
        cursor.execute("SELECT * FROM sources")
        rows = cursor.fetchall()
    finally:
        conn.close()
        
    configs_list = []
    
    # 2. Process each database row sequentially
    for row in rows:
        active_config = {}
        
        for key in row.keys():
            value = row[key]
            
            # Skip NULL
            if value is None:
                continue
                
            # convert stored string back to dict
            if key == "mapping" and isinstance(value, str):
                active_config[key] = json.loads(value)
            else:
                active_config[key] = value
                
        # Append the finalized, clean site configuration into our master list
        configs_list.append(active_config)
        
    return configs_list

# loop over all configs:
configs = fetch_all_configs()

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
    
    table_name = "articles"
    
    # 1. Create target data table using explicit, clean SQL definitions
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            title_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL UNIQUE,
            link TEXT,
            summary TEXT,
            date_captured TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cluster_id INTEGER
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
            INSERT OR IGNORE INTO {table_name} (source_id, title, link, summary)
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
    # Step 1: Loop over all available configs in the db
    configs = fetch_all_configs()
    for config in configs:
        active_config = config
        print(f"Extracting from {config['site_name']}")

        # Step 2: Ingest raw data via the scraping core
        raw_records = ez_parse(active_config)
    
        # Step 3: Pass data into the pandas filtering module
        cleaned_df = process_and_filter_records(raw_records)
    
        # Step 4: Stream unique data to SQL database file
        save_to_arachnet_db(cleaned_df, active_config)
