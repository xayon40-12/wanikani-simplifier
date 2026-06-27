#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error
import time

SUBJECTS_CACHE = "subjects_cache.json"
OUTPUT_FILE = "kanji_list.txt"
TOKEN_FILE = "token.txt"
API_URL = "https://api.wanikani.com/v2/subjects?types=kanji"

def get_api_token():
    # 1. Try environment variable
    token = os.environ.get("WANIKANI_API_TOKEN")
    if token:
        return token.strip()
        
    # 2. Try token.txt file
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                token = f.read().strip()
                if token:
                    return token
        except Exception as e:
            print(f"Error reading {TOKEN_FILE}: {e}")
            
    return None

def get_subjects(api_token, force_refresh=False):
    if not force_refresh and os.path.exists(SUBJECTS_CACHE):
        try:
            with open(SUBJECTS_CACHE, "r", encoding="utf-8") as f:
                print("Loading subjects from local cache...")
                return json.load(f)
        except Exception as e:
            print(f"Error reading cache: {e}. Fetching from API instead.")
            
    subjects = {}
    url = API_URL
    page = 1
    print("Fetching kanji subjects list from API...")
    while url:
        print(f"Fetching subjects page {page}...")
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {api_token}")
        req.add_header("User-Agent", "WaniKani Kanji Downloader/1.0 (python)")
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data.get("data", []):
                    sub_id = str(item.get("id"))
                    item_data = item.get("data", {})
                    char = item_data.get("characters")
                    if sub_id and char:
                        subjects[sub_id] = char
                url = data.get("pages", {}).get("next_url")
                page += 1
                time.sleep(0.1)
        except Exception as e:
            print(f"Error fetching subjects: {e}")
            break
            
    if subjects:
        try:
            with open(SUBJECTS_CACHE, "w", encoding="utf-8") as f:
                json.dump(subjects, f, ensure_ascii=False, indent=2)
            print(f"Cached {len(subjects)} subjects locally.")
        except Exception as e:
            print(f"Failed to write cache file: {e}")
            
    return subjects

def fetch_kanji_assignments(api_token):
    assigned_subject_ids = []
    # Apprentice 3 is SRS Stage 3. "At least Apprentice 3" means stages 3, 4, 5, 6, 7, 8, 9
    url = "https://api.wanikani.com/v2/assignments?subject_types=kanji&srs_stages=3,4,5,6,7,8,9"
    page = 1
    print("Fetching kanji assignments (at least Apprentice 3) from API...")
    while url:
        print(f"Fetching assignments page {page}...")
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {api_token}")
        req.add_header("User-Agent", "WaniKani Kanji Downloader/1.0 (python)")
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data.get("data", []):
                    sub_id = str(item.get("data", {}).get("subject_id"))
                    if sub_id:
                        assigned_subject_ids.append(sub_id)
                url = data.get("pages", {}).get("next_url")
                page += 1
                time.sleep(0.1)
        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            sys.exit(1)
        except Exception as e:
            print(f"Error fetching assignments: {e}")
            break
            
    print(f"Found {len(assigned_subject_ids)} assignments matching criteria.")
    return assigned_subject_ids

def main():
    token = get_api_token()
    force_refresh = False
    
    # Simple argument parsing
    args = sys.argv[1:]
    if "--refresh" in args:
        force_refresh = True
        args.remove("--refresh")
    
    if args:
        token = args[0]
        
    if not token:
        print("Error: WaniKani API token not found.")
        print(f"Please set the WANIKANI_API_TOKEN environment variable or put it in a file named '{TOKEN_FILE}'.")
        sys.exit(1)
        
    subjects = get_subjects(token, force_refresh)
    if not subjects:
        print("Error: Could not load WaniKani subjects.")
        sys.exit(1)
        
    assigned_ids = fetch_kanji_assignments(token)
    
    # Map assignment IDs to characters
    matched_kanji = []
    for sub_id in assigned_ids:
        char = subjects.get(sub_id)
        if char:
            matched_kanji.append(char)
        else:
            print(f"Warning: Subject ID {sub_id} not found in subjects cache.")
            
    # Save to file
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for char in matched_kanji:
                f.write(f"{char}\n")
        print(f"Saved {len(matched_kanji)} kanji characters to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
