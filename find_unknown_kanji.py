#!/usr/bin/env python3
import sys
import os
import subprocess

KANJI_LIST_FILE = "kanji_list.txt"
FETCH_KANJI_SCRIPT = "fetch_kanji.py"

def update_kanji_list():
    print("Updating known kanji list from WaniKani...")
    if not os.path.exists(FETCH_KANJI_SCRIPT):
        print(f"Error: {FETCH_KANJI_SCRIPT} not found in the current directory.")
        sys.exit(1)
        
    try:
        # Run fetch_kanji.py as a subprocess to update the list
        subprocess.run([sys.executable, FETCH_KANJI_SCRIPT], check=True)
        print("Kanji list updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {FETCH_KANJI_SCRIPT}: {e}")
        sys.exit(1)

def load_known_kanji():
    if not os.path.exists(KANJI_LIST_FILE):
        print(f"Error: {KANJI_LIST_FILE} not found after update attempt.")
        sys.exit(1)
        
    known = set()
    with open(KANJI_LIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            char = line.strip()
            if char:
                known.add(char)
    print(f"Loaded {len(known)} known kanji from {KANJI_LIST_FILE}.")
    return known

def is_kanji(char):
    # Standard Japanese Kanji range (CJK Unified Ideographs)
    return '\u4e00' <= char <= '\u9fff'

def analyze_file(filepath, known_kanji):
    if not os.path.exists(filepath):
        print(f"Error: Target file {filepath} not found.")
        sys.exit(1)
        
    unknown_occurrences = []
    unique_unknown = set()
    
    print(f"Analyzing {filepath} for unknown kanji...")
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            for char_num, char in enumerate(line, 1):
                if is_kanji(char) and char not in known_kanji:
                    unknown_occurrences.append((line_num, char_num, char))
                    unique_unknown.add(char)
                    
    return unknown_occurrences, unique_unknown

def main():
    if len(sys.argv) < 2:
        print("Usage: ./find_unknown_kanji.py <target_text_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    
    # 1. Update the known kanji list
    update_kanji_list()
    
    # 2. Load the known kanji
    known_kanji = load_known_kanji()
    
    # 3. Analyze target file
    occurrences, unique = analyze_file(target_file, known_kanji)
    
    print("\n" + "=" * 40)
    print(f"RESULTS FOR: {target_file}")
    print(f"Found {len(occurrences)} unknown kanji occurrences ({len(unique)} unique characters).")
    print("=" * 40)
    
    if occurrences:
        for line, col, char in occurrences:
            print(f"Line {line:3d}, Column {col:2d}: {char}")
    else:
        print("All kanji in this file are in your known list!")

if __name__ == "__main__":
    main()
