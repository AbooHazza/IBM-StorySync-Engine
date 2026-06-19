import os
import re
import time
import json
from dotenv import load_dotenv
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions

# Load environment variables
load_dotenv()

# File Configuration
SUBTITLE_FILE = os.getenv("SUBTITLE_FILE", "eps1.0_hellofriend.mov subtitles English _ opensubtitles.com.srt")
DATA_FILE = os.getenv("DATA_FILE", "data.json")
EPISODE_NUM = 1
SEASON_NUM = 1

def parse_time_to_seconds(time_str):
    """Converts SRT timestamp (HH:MM:SS,mmm) to total seconds."""
    time_str = time_str.replace(',', '.')  # Handle comma as decimal point
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def parse_srt(file_path):
    """Parses a standard .srt file into a list of subtitle dictionaries."""
    print(f"Parsing subtitle file: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Subtitle file not found at {file_path}")
        
    with open(file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        content = f.read()

    # Split by double newlines to separate subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # We want to make sure the second line is a timestamp line
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1].strip())
            if timestamp_match:
                start_sec = parse_time_to_seconds(timestamp_match.group(1))
                end_sec = parse_time_to_seconds(timestamp_match.group(2))
                text = " ".join([l.strip() for l in lines[2:] if l.strip()])
                
                # Clean up HTML tags from text
                text = re.sub(r'<[^>]*>', '', text)
                
                subtitles.append({
                    "start": start_sec,
                    "end": end_sec,
                    "text": text
                })
                
    print(f"Parsed {len(subtitles)} subtitle lines.")
    return subtitles

def group_subtitles_by_minute(subtitles):
    """Groups parsed subtitles into 1-minute (60-second) chronological chunks."""
    print("Grouping subtitles into 1-minute chunks...")
    if not subtitles:
        return {}
        
    max_time = max([sub['end'] for sub in subtitles])
    total_minutes = int(max_time // 60) + 1
    
    # Initialize bins
    chunks = {i: [] for i in range(total_minutes)}
    
    for sub in subtitles:
        # Determine which minute bin this subtitle belongs to based on its start time
        bin_idx = int(sub['start'] // 60)
        if bin_idx in chunks:
            chunks[bin_idx].append(sub['text'])
            
    # Concatenate texts in each bin
    grouped_chunks = {}
    for minute, text_list in chunks.items():
        grouped_chunks[minute] = " ".join(text_list).strip()
        
    return grouped_chunks

def extract_entities_nlu(text, nlu_client):
    """Uses Watson NLU to extract entities from a block of text."""
    # If the text is empty or very short, skip NLU to save credits and avoid errors
    if not text or len(text.strip()) < 15:
        return []
        
    try:
        response = nlu_client.analyze(
            text=text,
            features=Features(entities=EntitiesOptions(limit=20))
        ).get_result()
        
        # Pull out entity text and deduplicate
        entities = list(set([ent['text'] for ent in response.get('entities', [])]))
        return entities
    except Exception as e:
        print(f"[NLU Warning] Failed to analyze text chunk: {e}")
        return []

def save_to_local_json(documents):
    """Saves enriched documents to a local JSON file."""
    print(f"Saving {len(documents)} documents to {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(documents)} documents to {DATA_FILE}.")
    except Exception as e:
        raise RuntimeError(f"Failed to write local data file: {e}")

def main():
    # 1. Initialize Watson NLU Client
    nlu_key = os.getenv("NLU_API_KEY")
    nlu_url = os.getenv("NLU_URL")
    
    if not nlu_key or not nlu_url:
        print("[FAIL] Watson NLU credentials missing in .env")
        return
        
    nlu_authenticator = IAMAuthenticator(nlu_key)
    nlu_client = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=nlu_authenticator
    )
    nlu_client.set_service_url(nlu_url)
    
    # 2. Parse Subtitles
    try:
        subtitles = parse_srt(SUBTITLE_FILE)
    except Exception as e:
        print(f"[FAIL] Error parsing SRT file: {e}")
        return
        
    # 3. Group by minute
    grouped_chunks = group_subtitles_by_minute(subtitles)
    
    # 4. Enrich chunks with NLU
    print("Enriching text chunks with Watson NLU...")
    documents = []
    
    for minute, text in grouped_chunks.items():
        print(f"Processing minute {minute}... ", end="", flush=True)
        if text:
            # Extract entities
            entities = extract_entities_nlu(text, nlu_client)
            
            # Embeddings are not available in the current IBM SDK, so use an empty placeholder.
            embedding_vector = []

            doc = {
                "episode": EPISODE_NUM,
                "season": SEASON_NUM,
                "start_time_sec": minute * 60,
                "end_time_sec": (minute + 1) * 60,
                "text": text,
                "entities": entities,
                "embedding": embedding_vector
            }
            documents.append(doc)
            print(f"Done (extracted {len(entities)} entities)")
            
            # Simple rate limiting/polite delay for NLU API calls
            time.sleep(0.2)
        else:
            print("Empty (Skipped NLU)")
            doc = {
                "episode": EPISODE_NUM,
                "season": SEASON_NUM,
                "start_time_sec": minute * 60,
                "end_time_sec": (minute + 1) * 60,
                "text": "",
                "entities": [],
                "embedding": []
            }
            documents.append(doc)

    # 5. Save to local JSON storage
    try:
        save_to_local_json(documents)
        print("Ingestion pipeline completed successfully! Local data is ready.")
    except Exception as e:
        print(f"[FAIL] Local data storage failed: {e}")

if __name__ == "__main__":
    main()
