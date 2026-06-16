# To test your data within Python or a notebook environment, practice your bootcamp commands:
import sqlite3
import pandas as pd

conn = sqlite3.connect("arachnet.db")

# Practice filtering metrics based on specific sources or words
query = "SELECT source_site, headline FROM economy_news_feed WHERE headline LIKE '%market%' ORDER BY date_captured DESC;"
test_df = pd.read_sql_query(query, conn)

print(test_df.head())
conn.close()