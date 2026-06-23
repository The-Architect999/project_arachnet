import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer # Term Frequency-Inverse Document Frequency
from sklearn.metrics.pairwise import cosine_similarity # metric for semantic similarity orientation
from rapidfuzz import distance # C++ optimized string matching
from datetime import datetime, timedelta
import json


def compute_jaccard(str1, str2):
    """Computes word-level token overlap using optimized native sets."""
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    intersection = words1.intersection(words2) 
    union = words1.union(words2) 
    return len(intersection) / len(union) if union else 0.0 # common unique words / total unique words


def process_and_cluster_all_pairs(articles, max_hours_gap=72):
    """
    Accepts a list of dictionaries representing database records:
    [{"db_id": 1, "title": "...", "summary": "...", "published_at": datetime}, ...]
    """
    if not articles:
        return []
    
    # 1. Vectorize raw text inputs into TF-IDF spaces (Using Titles and summary both for rich semantic density)
    combined_text = [f"{item['title']} {item['summary']}" for item in articles]
    vectorizer = TfidfVectorizer(stop_words='english') # ignore common English filler words ("and", "the", "is", "over")
    tfidf_matrix = vectorizer.fit_transform(combined_text) # convert entire raw summary stack into numerical matrix
    
    clusters = [] # stores index allocations: [[0, 1], [2, 4], [3]]

    # 2. Clustering loop
    for idx, current_item in enumerate(articles): # index over articles for memory optimization
        current_vector = tfidf_matrix[idx] # isolate vector profile for current summary
        current_title = current_item["title"]
        current_date = current_item["published_at"]
        
        # Ensure date is a valid Python datetime object
        if isinstance(current_date, str):
            current_date = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
            
        placed = False
        best_score_overall = 0.0
        best_cluster_match = None

        # Iterate through every cluster currently established
        for cluster in clusters:
            # Anchor article profile extraction
            anchor_article = articles[cluster[0]]
            anchor_date = anchor_article["published_at"]
            if isinstance(anchor_date, str):
                anchor_date = datetime.strptime(anchor_date, "%Y-%m-%d %H:%M:%S")
            
            # FRESHNESS GATE (3 day window)
            if abs(current_date - anchor_date) > timedelta(hours=max_hours_gap):
                continue # Skip computing heavy matrix scores for historically distant topics
                
            cluster_vectors = tfidf_matrix[cluster] # vector profiles for current cluster
            cosine_scores = cosine_similarity(current_vector, cluster_vectors)[0]
            max_cluster_score = np.max(cosine_scores) # locate highest match in this specific group
            
            # Keep track of the highest score across ALL clusters
            if max_cluster_score > best_score_overall:
                best_score_overall = max_cluster_score
                best_cluster_match = cluster 

        # EVALUATION GATE: Only evaluate if a valid semantic cluster anchor was found
        if best_cluster_match and best_score_overall > 0.15: # Raised threshold for high-density summaries
            best_cluster_master_text = articles[best_cluster_match[0]]["title"]
            
            # Filter with Levenshtein before appending (Using TITLES for precision verification)
            inline_lev = distance.Levenshtein.normalized_similarity(best_cluster_master_text.lower(), current_title.lower())
            
            if inline_lev > 0.35: # Structural tolerance threshold adjusted for title rephrasings
                best_cluster_match.append(idx)
                placed = True
                
        if not placed:
            # New cluster (triggered if Cosine failed OR if Levenshtein gate rejected it)
            clusters.append([idx])

    # 3. Layering Jaccard & Levenshtein Metrics Across Clusters
    final_output = []
    '''payload storage container for database engine or API delivery'''

    for cluster in clusters:
        anchor_article = articles[cluster[0]]
        master_title = anchor_article["title"] # the very first headline that spawned the cluster
        
        variants_breakdown = [] # granular container to compile individual verification metrics per string variant
        cluster_dates = []
        
        for i in cluster:
            variant_item = articles[i]
            variant_title = variant_item["title"]
            variant_date = variant_item["published_at"]
            if isinstance(variant_date, str):
                variant_date = datetime.strptime(variant_date, "%Y-%m-%d %H:%M:%S")
            cluster_dates.append(variant_date)
            
            # Character-level edit distance calculation tracking typos, spelling alterations, or structural changes
            lev_sim = distance.Levenshtein.normalized_similarity(master_title.lower(), variant_title.lower())
            
            # Word-level token intersection calculation
            jaccard_sim = compute_jaccard(master_title, variant_title)
            
            # Compile individual title metrics
            variants_breakdown.append({
                "db_serial_number": variant_item["db_id"], # Reference tracking pointer back to SQL primary key
                "headline_text": variant_title,
                "published_time": variant_date.strftime("%Y-%m-%d %H:%M:%S"),
                "raw_metrics": {
                    "levenshtein_similarity": round(lev_sim, 2),
                    "jaccard_similarity": round(jaccard_sim, 2)
                }
            })
        
        # Append the clustered topic block along with its dynamic volume metrics to the final array
        final_output.append({
            "cluster_anchor_db_id": anchor_article["db_id"],
            "cluster_master": master_title,
            "volume_count": len(cluster),
            "latest_update_time": max(cluster_dates).strftime("%Y-%m-%d %H:%M:%S"),
            "metrics_payload": variants_breakdown
        })
        
    return final_output


# ==========================================
# SIMULATED DB WITHDRAWAL TESTING
# ==========================================
if __name__ == "__main__":
    # Mock data structure matching a standard row dictionary retrieval from database
    mock_db_records = [
        {
            "db_id": 1001,
            "title": "RBI keeps repo rate unchanged in latest policy meet",
            "summary": "The Reserve Bank of India maintained status quo on the key repo rate in its meeting today, keeping it steady to ensure macroeconomic parameters align with inflation targets.",
            "published_at": "2026-06-22 10:00:00"
        },
        {
            "db_id": 1002,
            "title": "RBI holding repo rate steady amid macro stability concerns",
            "summary": "Citing ongoing global challenges and macroeconomic stability concerns, the RBI decided to keep the benchmark repo rate completely unchanged during its latest monetary policy review.",
            "published_at": "2026-06-22 10:15:00"
        },
        {
            "db_id": 1003,
            "title": "Central bank keeps key repo rate steady to manage inflation pressures",
            "summary": "India's central bank kept its primary lending rate unchanged today. The monetary policy committee focused on curbing sticky retail inflation while supporting structural growth metrics.",
            "published_at": "2026-06-22 11:30:00"
        },
        {
            "db_id": 1004,
            "title": "Markets tank 500 points on global geopolitical tensions",
            "summary": "Domestic equity indices crashed sharply today as indices dropped over 500 points. Investors locked in profits following escalating geopolitical tensions across key trade corridors.",
            "published_at": "2026-06-22 12:00:00"
        }
    ]
    
    analysis_report = process_and_cluster_all_pairs(mock_db_records)
    print(json.dumps(analysis_report, indent=4))
