import os
import re
import json
from collections import Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "data.json")

def load_local_data():
    """Reads the local JSON dataset produced by data_parser."""
    if not os.path.exists(DATA_FILE):
        print(f"[Local Data] {DATA_FILE} not found.")
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[Local Data] Failed to load {DATA_FILE}: {e}")
        return []


def parse_time_str_to_seconds(time_str):
    """Parses HH:MM:SS or MM:SS to total seconds."""
    parts = time_str.strip().split(':')
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    else:
        return float(parts[0])

def retrieve_safe_chunks(user_pause_time_sec):
    """Loads local data and returns only chunks that are safe for the current paused timestamp."""
    all_chunks = load_local_data()
    safe_chunks = []
    for chunk in all_chunks:
        if chunk.get('episode') == 1 and chunk.get('start_time_sec') is not None:
            if chunk['start_time_sec'] <= user_pause_time_sec:
                safe_chunks.append(chunk)
    print(f"[Spoiler Shield] Local dataset query retained {len(safe_chunks)} safe chunks.")
    return safe_chunks

def normalize_text(text):
    """Normalize text into lowercase tokens."""
    return re.findall(r"\w+", text.lower())

def text_vector(text):
    """Converts a text string to a token frequency vector."""
    return Counter(normalize_text(text))

def cosine_similarity(vec1, vec2):
    """Calculates cosine similarity between two token-frequency vectors."""
    if not vec1 or not vec2:
        return 0.0

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[token] * vec2[token] for token in intersection)
    sum1 = sum(value * value for value in vec1.values())
    sum2 = sum(value * value for value in vec2.values())
    if sum1 == 0 or sum2 == 0:
        return 0.0

    return numerator / ((sum1 ** 0.5) * (sum2 ** 0.5))


def calculate_relevance_score(query_text, chunk_text, query_lower, entities):
    """Calculates a fallback semantic score using local text similarity and metadata bonus."""
    if not query_text or not chunk_text:
        return 0.0

    score = cosine_similarity(text_vector(query_text), text_vector(chunk_text))
    score *= 100.0

    for entity in entities:
        if entity.lower() in query_lower:
            score += 15.0

    return score

def classify_intent(user_query):
    """Classify the user's intent as either 'SUMMARIZE' or 'QUESTION'."""
    from generation_engine import get_watsonx_model
    
    prompt = f"""Classify the following user query as either 'SUMMARIZE' (asking for lore, summary, recap) or 'QUESTION' (specific detail).
Query: "{user_query}"
Respond with ONLY the word SUMMARIZE or QUESTION.
Classification:"""
    try:
        model = get_watsonx_model(max_tokens=10)
        response = model.generate(prompt=prompt)
        intent = response['results'][0]['generated_text'].strip().upper()
        if "SUMMARIZE" in intent:
            return "SUMMARIZE"
        return "QUESTION"
    except Exception as e:
        print(f"[Intent Classifier Error] {e}")
        return "QUESTION"

def get_rag_context(user_query, user_pause_time_sec):
    """
    Implements the Dynamic RAG Pipeline:
    1. Triggers the Spoiler Shield to drop future data.
    2. Separates the current active minute (Immediate Context).
    3. Finds the top 3 historically relevant chunks via hybrid scoring.
    """
    # 1. Enforce the Spoiler Shield
    safe_chunks = retrieve_safe_chunks(user_pause_time_sec)
    
    if not safe_chunks:
        return {
            "immediate": None,
            "historical": [],
            "combined_context": "No watched history available for this timestamp.",
            "intent": "UNKNOWN"
        }
        
    intent = classify_intent(user_query)
    print(f"[Intent Classifier] Query intent detected as: {intent}")
    
    immediate_chunk = None
    historical_pool = []
    
    # 3. Partition chunks into Immediate and Historical
    for chunk in safe_chunks:
        start = chunk['start_time_sec']
        end = chunk['end_time_sec']
        
        # Check if this chunk is what the user is currently watching
        if start <= user_pause_time_sec < end:
            immediate_chunk = chunk
        else:
            historical_pool.append(chunk)

    top_historical = []

    if intent == 'SUMMARIZE':
        print("[Intent Classifier] SUMMARIZE intent detected. Skipping vector search and returning all historical context.")
        top_historical = historical_pool.copy()
    else:
        # 2. Use local text similarity for semantic search fallback
        print(f"Scoring query against historical dialogue for: '{user_query}'...")
        scored_history = []
        query_lower = user_query.lower()
        
        for chunk in historical_pool:
            score = calculate_relevance_score(
                user_query,
                chunk.get('text', ''),
                query_lower,
                chunk.get('entities', [])
            )
            scored_history.append((score, chunk))
            
        # Sort by score descending
        scored_history.sort(key=lambda x: x[0], reverse=True)
        
        print("\n--- [RAG Text Similarity Scores] ---")
        for score, chunk in scored_history:
            if score >= 20.0:
                min_start = chunk['start_time_sec'] // 60
                print(f"Minute {min_start:02d} | Score: {score:.2f} | Entities: {chunk.get('entities')}")
                top_historical.append(chunk)
        print("---------------------------\n")

    # 4. Formulate the clean prompt context
    context_lines = []
    
    if immediate_chunk:
        min_start = immediate_chunk['start_time_sec'] // 60
        context_lines.append(f"=== IMMEDIATE SCENE CONTEXT (MINUTE {min_start}) ===")
        context_lines.append(f"[Minute {min_start}]: {immediate_chunk['text']}")
    else:
        context_lines.append("=== IMMEDIATE SCENE CONTEXT (NO DIALOGUE) ===")
        context_lines.append("(No dialogue in the immediate past minute)")
        
    context_lines.append("\n=== HISTORICAL CONTEXT ===")
    if top_historical:
        # Sort historical chunks chronologically for logical LLM consumption
        top_historical.sort(key=lambda x: x['start_time_sec'])
        for chunk in top_historical:
            min_start = chunk['start_time_sec'] // 60
            context_lines.append(f"[Minute {min_start}]: {chunk['text']}")
    else:
        context_lines.append("(No relevant historical context found)")
        
    combined_context = "\n".join(context_lines)
    return {
        "immediate": immediate_chunk,
        "historical": top_historical,
        "combined_context": combined_context,
        "intent": intent
    }

if __name__ == "__main__":
    # Test connection and local scoring logic
    print("Testing Retrieval Engine...")
    test_query = "Who is Rohit and what is his website?"
    test_pause_time = "02:30"  # 150 seconds
    
    pause_sec = parse_time_str_to_seconds(test_pause_time)
    print(f"Simulating video paused at {test_pause_time} ({pause_sec} seconds)")
    
    result = get_rag_context(test_query, pause_sec)
    print("Combined Context sent to LLM:")
    print("====================================================")
    print(result['combined_context'])
    print("====================================================")
