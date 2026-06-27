#!/usr/bin/env python3
import sys
import os
import re
import subprocess

KANJI_LIST_FILE = "kanji_list.txt"
MASTERED_FILE = "mastered_kanji.txt"
CUSTOM_KNOWN_FILE = "custom_known_kanji.txt"
CUSTOM_MASTERED_FILE = "custom_mastered_kanji.txt"
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

def load_kanji_list(filepath):
    if not os.path.exists(filepath):
        return set()
    known = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            # Ignore empty lines and comment lines
            if line_str and not line_str.startswith("#"):
                # Take only the first character (in case of side comments)
                char = line_str[0]
                if is_kanji(char):
                    known.add(char)
    return known

def is_kanji(char):
    # Standard Japanese Kanji range (CJK Unified Ideographs)
    return '\u4e00' <= char <= '\u9fff'

def offset_to_line_col(content, offset):
    before = content[:offset]
    lines = before.split("\n")
    line_num = len(lines)
    col_num = len(lines[-1]) + 1
    return line_num, col_num

def analyze_file(filepath, known_kanji, mastered_kanji):
    if not os.path.exists(filepath):
        print(f"Error: Target file {filepath} not found.")
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    errors = []
    unmastered = known_kanji - mastered_kanji
    
    # 1. Parse ruby blocks: <ruby>KANJI<rt>READING</rt></ruby>
    ruby_pattern = re.compile(r'<ruby>(?P<kanji>[^<]+)<rt>(?P<reading>[^<]+)</rt></ruby>')
    ruby_intervals = []
    
    for match in ruby_pattern.finditer(content):
        start, end = match.span()
        ruby_intervals.append((start, end))
        kanji_str = match.group("kanji")
        
        # Check if the kanji inside the ruby block are known at all
        for char in kanji_str:
            if is_kanji(char) and char not in known_kanji:
                char_offset = start + content[start:end].find(char)
                line, col = offset_to_line_col(content, char_offset)
                errors.append((line, col, char, "Unknown kanji inside ruby tag"))

    def is_inside_ruby(offset):
        for start, end in ruby_intervals:
            if start <= offset < end:
                return True
        return False

    # 2. Check all characters in the text
    for offset, char in enumerate(content):
        if is_inside_ruby(offset):
            continue
            
        if is_kanji(char):
            line, col = offset_to_line_col(content, offset)
            if char not in known_kanji:
                errors.append((line, col, char, "Unknown kanji"))
            elif mastered_kanji and char in unmastered:
                errors.append((line, col, char, "Unmastered kanji missing <ruby> tags"))
                
    errors.sort()
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: ./find_unknown_kanji.py <target_text_file>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    
    # 1. Update the known kanji list
    update_kanji_list()
    
    # 2. Load lists
    known_kanji = load_kanji_list(KANJI_LIST_FILE)
    mastered_kanji = load_kanji_list(MASTERED_FILE)
    
    # Load custom lists
    custom_known = load_kanji_list(CUSTOM_KNOWN_FILE)
    custom_mastered = load_kanji_list(CUSTOM_MASTERED_FILE)
    
    # Merge
    known_kanji.update(custom_known)
    mastered_kanji.update(custom_mastered)
    
    if not known_kanji:
        print(f"Error: Could not load {KANJI_LIST_FILE}.")
        sys.exit(1)
        
    if not mastered_kanji:
        print("Warning: mastered_kanji.txt not found. Skipping ruby tag verification.")
        
    # 3. Analyze target file
    errors = analyze_file(target_file, known_kanji, mastered_kanji)
    
    print("\n" + "=" * 50)
    print(f"RESULTS FOR: {target_file}")
    print("=" * 50)
    
    if errors:
        unknown_count = sum(1 for e in errors if "Unknown" in e[3])
        missing_ruby_count = sum(1 for e in errors if "missing" in e[3])
        
        print(f"Found {len(errors)} issues:")
        if unknown_count:
            print(f"  - {unknown_count} unknown kanji")
        if missing_ruby_count:
            print(f"  - {missing_ruby_count} unmastered kanji missing <ruby> tags")
        print("-" * 50)
        
        for line, col, char, message in errors:
            print(f"Line {line:3d}, Column {col:2d}: {char} -> {message}")
    else:
        print("All kanji in this file are in your known list, and unmastered ones have ruby tags!")

if __name__ == "__main__":
    main()
