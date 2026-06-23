from datetime import datetime
import sqlite3
import nltk

# If VADER lexicon package not found, download locally
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

# instanciate VADER sentiment once globally
sia = SentimentIntensityAnalyzer()

def calculate_time_decay(previous_score, last_evaluated_at):
    """
    Applies a 33.33% daily reduction based on elapsed seconds.
    """
    now = datetime.now()
    elapsed_seconds = (now - last_evaluated_at).total_seconds()
    
    days_elapsed = elapsed_seconds / 86400.0
    
    decay_factor = (0.666667) ** days_elapsed
    
    # returns score with decay applied
    final_score = previous_score * decay_factor
    
    return final_score


def evaluate_trend_scoring(cluster_payloads, existing_scores_map):
    """
    Core engine for scoring trends based on cluster volume, token cohesion, 
    and an averaged cluster sentiment profile.
    
    existing_scores_map: Dictionary mapping existing database states:
                        { cluster_anchor_db_id: {"score": float, "last_evaluated_at": datetime} }
    """
    now = datetime.now()
    scoring_actions = []

    for cluster in cluster_payloads:
        cluster_id = cluster["cluster_anchor_db_id"]
        volume = cluster["volume_count"]
        variants = cluster["metrics_payload"]
        
        # 1. Get avg jaccard
        jaccard_scores = [item["raw_metrics"]["jaccard_similarity"] for item in variants]
        avg_jaccard = sum(jaccard_scores) / len(jaccard_scores) if jaccard_scores else 1.0
        
        # 2. COMPUTE CLUSTER-WIDE AVERAGE SENTIMENT
        sentiment_scores = []
        for item in variants:
            # Analyze text field with dense vocabulary (summary falls back to title text)
            text_to_analyze = item.get("summary_text") or item.get("headline_text") or ""
            
            # Run VADER lexicon mapping
            polarity = sia.polarity_scores(text_to_analyze)
            sentiment_scores.append(polarity["compound"]) # Bounded between -1.0 and 1.0
            
        # Calculate strict arithmetic mean of sentiment across the entire cluster
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # 3. COMPUTE THE NEW INCOMING SURGE ENERGY
        # Non-linear saturation curve: scales smoothly with max multiplier - 1.0
        volume_saturation = volume / (volume + 2.0)
        loop_surge_score = avg_sentiment * volume_saturation * avg_jaccard
        
        # 4. TIME DILATION & HISTORICAL COMPOUNDING
        if cluster_id in existing_scores_map:
            # Score exists in DB: Pull data and decay it based on time delta
            historical = existing_scores_map[cluster_id]
            decayed_base_score = calculate_time_decay(historical["score"], historical["last_evaluated_at"])
            
            # Compound: Add fresh surge energy directly to the decayed baseline
            final_score = decayed_base_score + loop_surge_score
            # Hard limit guardrails to prevent numeric overflow outside VADER boundaries
            final_score = max(-1.0, min(1.0, final_score))
        else:
            # Fresh score
            final_score = max(-1.0, min(1.0, loop_surge_score))
            
        # 5. STRUCTURE PAYLOAD FOR THE MASTER FILE EXECUTION LAYER
        # If a trend decays completely to 0.0, flag it for physical removal from the DB
        is_dead = abs(final_score) < 0.001
        
        scoring_actions.append({
            "cluster_id": cluster_id,
            "calculated_score": 0.0 if is_dead else round(final_score, 4),
            "avg_sentiment": round(avg_sentiment, 4),
            "avg_jaccard": round(avg_jaccard, 4),
            "evaluated_at": now,
            "action": "DELETE" if is_dead else "UPSERT"
        })
        
    return scoring_actions


# ==========================================
# DATABASE STORAGE MANAGEMENT LAYER
# ==========================================
def fetch_clustering_payloads_from_db(db_path="arachnet.db"):
    """
    Assembles relational macro clusters by grouping article variants by cluster_id.
    Calculates the dynamic structural volume count per group from the raw records.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cluster_payloads = []
    
    try:
        # Pull all matched article instances clustered in the relational layer
        cursor.execute("""
            SELECT 
                cluster_id,
                title_id AS db_serial_number,
                title AS headline_text,
                summary AS summary_text
            FROM articles
            WHERE cluster_id IS NOT NULL
            ORDER BY cluster_id;
        """)
        rows = cursor.fetchall()
        
        # Build dictionary groups tracking article collections under their respective cluster IDs
        grouped_data = {}
        for row in rows:
            c_id = row["cluster_id"]
            if c_id not in grouped_data:
                grouped_data[c_id] = {
                    "cluster_anchor_db_id": c_id,
                    "metrics_payload": []
                }
            
            grouped_data[c_id]["metrics_payload"].append({
                "db_serial_number": row["db_serial_number"],
                "headline_text": row["headline_text"],
                "summary_text": row["summary_text"],
                "raw_metrics": {
                    "jaccard_similarity": 1.0  # Fallback baseline weight for internal evaluation loops
                }
            })
            
        # Dynamically inject the volume count based on total grouped child elements
        for c_id, payload in grouped_data.items():
            payload["volume_count"] = len(payload["metrics_payload"])
            cluster_payloads.append(payload)
            
    except sqlite3.Error as e:
        print(f"[SQL Ingestion Alert] Could not resolve clustered payload grouping: {e}")
    finally:
        conn.close()
        
    return cluster_payloads


def fetch_historical_scores_map(db_path="arachnet.db"):
    """
    Queries the database for existing active scores and their evaluation timestamps.
    Returns a dictionary mapping: { cluster_id: {"score": float, "last_evaluated_at": datetime} }
    """
    conn = sqlite3.connect(db_path)
    
    existing_scores_map = {}
    
    try:
        # Check table columns to prevent operational failures on fresh setups
        cursor_setup = conn.cursor()
        cursor_setup.execute("PRAGMA table_info(clusters);")
        columns = [col[1] for col in cursor_setup.fetchall()]
        cursor_setup.close()
        
        if "score" in columns and "cluster_id" in columns:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cluster_id, score, last_updated 
                FROM clusters
                WHERE score IS NOT NULL AND last_updated IS NOT NULL;
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                try:
                    dt_obj = datetime.strptime(row["last_updated"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt_obj = datetime.now()
                    
                existing_scores_map[row["cluster_id"]] = {
                    "score": float(row["score"]),
                    "last_evaluated_at": dt_obj
                }
            cursor.close()
    except sqlite3.Error as e:
        print(f"[SQL Score Fetch Debug] Notice: {e}")
    finally:
        conn.close()
        
    return existing_scores_map


def save_trend_scoring_actions(scoring_actions, db_path="arachnet.db"):
    """
    Applies the actions generated by evaluate_trend_scoring directly to the database.
    Handles structural column additions, updates metrics, and purges completely decayed dead records.
    """
    if not scoring_actions:
        print("[SQL Score Writer] No tracking updates to process.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Guarantee structural tracking columns exist in clusters
        cursor.execute("PRAGMA table_info(clusters);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "score" not in columns:
            cursor.execute("ALTER TABLE clusters ADD COLUMN score REAL DEFAULT 0.0;")
        if "avg_sentiment" not in columns:
            cursor.execute("ALTER TABLE clusters ADD COLUMN avg_sentiment REAL DEFAULT 0.0;")
        if "avg_jaccard" not in columns:
            cursor.execute("ALTER TABLE clusters ADD COLUMN avg_jaccard REAL DEFAULT 0.0;")

        # Separate actions for high-speed batch execution profiles
        upsert_batch = []
        delete_batch = []

        for item in scoring_actions:
            formatted_time = item["evaluated_at"].strftime("%Y-%m-%d %H:%M:%S")
            
            if item["action"] == "DELETE":
                delete_batch.append((item["cluster_id"],))
            else:
                upsert_batch.append((
                    item["calculated_score"],
                    item["avg_sentiment"],
                    item["avg_jaccard"],
                    formatted_time,
                    item["cluster_id"]
                ))

        # Fire atomic batch updates
        if upsert_batch:
            cursor.executemany("""
                UPDATE clusters
                SET score = ?,
                    avg_sentiment = ?,
                    avg_jaccard = ?,
                    last_updated = ?
                WHERE cluster_id = ?;
            """, upsert_batch)
            print(f"[SQL Score Writer] Successfully updated trend profiles for {len(upsert_batch)} rows.")

        if delete_batch:
            cursor.executemany("""
                DELETE FROM clusters WHERE cluster_id = ?;
            """, delete_batch)
            print(f"[SQL Score Writer] Purged {len(delete_batch)} completely dead/decayed macro rows.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"[SQL Score Writer Critical Error] Rolling back active transaction: {e}")
        conn.rollback()
    finally:
        conn.close()


# ==========================================
# LOCAL STANDALONE ENGINE SIMULATION
# ==========================================
if __name__ == "__main__":
    import json
    
    # Mocking data coming straight out of your clustering engine module
    mock_clustering_output = [
        {
            "cluster_anchor_db_id": 5501,
            "cluster_master": "Markets tank 500 points on global geopolitical tensions",
            "volume_count": 2,
            "latest_update_time": "2026-06-22 10:00:00",
            "metrics_payload": [
                {
                    "db_serial_number": 101,
                    "headline_text": "Markets tank 500 points on global geopolitical tensions",
                    "summary_text": "Domestic equity indices crashed sharply today as stock benchmarks dropped over 500 points. Severe financial devastation feared as oil supply corridors face military blockades.",
                    "raw_metrics": {"levenshtein_similarity": 1.0, "jaccard_similarity": 1.0}
                },
                {
                    "db_serial_number": 102,
                    "headline_text": "Sensex crashes 500 pts as supply lines choke",
                    "summary_text": "Markets posted massive red candles today. Panic selling accelerated following terrible geopolitical gridlocks, wounding retail investor portfolios across the country.",
                    "raw_metrics": {"levenshtein_similarity": 0.42, "jaccard_similarity": 0.38}
                }
            ]
        }
    ]
    
    # Mock database state mapping table for existing active scores
    # This simulates a story that broke earlier and already has a decaying score tracked
    mock_existing_scores_db = {
        5501: {
            "score": -0.4500, 
            "last_evaluated_at": datetime.strptime("2026-06-21 10:00:00", "%Y-%m-%d %H:%M:%S") # Exactly 24 hours ago
        }
    }
    
    # print("--- Running Score and Store Engine Simulation ---")
    # actions = evaluate_trend_scoring(mock_clustering_output, mock_existing_scores_db)
    # print(json.dumps(actions, indent=4, default=str))

    '''
    real data test
    '''
    print("--- Running Score and Store Engine Simulation ---")
    
    # Fetch clusters data payloads and historical records maps
    payloads_data = fetch_clustering_payloads_from_db(db_path="arachnet.db")
    historical_map = fetch_historical_scores_map(db_path="arachnet.db")
    
    # Run structural arithmetic evaluations
    actions = evaluate_trend_scoring(payloads_data, historical_map)
    print(json.dumps(actions, indent=4, default=str))
    
    # Commit execution steps to live SQLite tables
    print("\n--- Committing Scores and Analytics Columns to Database ---")
    save_trend_scoring_actions(actions, db_path="arachnet.db")