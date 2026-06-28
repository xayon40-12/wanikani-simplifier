#!/usr/bin/env python3
import os
import re

# Resolve paths relative to this script's location (root folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSONAL_DIR = os.path.join(BASE_DIR, "personal")
NOVELS_DIR = os.path.join(PERSONAL_DIR, "novels")
ROOT_README = os.path.join(PERSONAL_DIR, "README.md")

def parse_chapter_title(filepath):
    if not os.path.exists(filepath):
        return "Untitled"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Title:"):
                    return line.replace("Title:", "").strip()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return "Untitled"

def init_readmes():
    if not os.path.exists(NOVELS_DIR):
        print("No novels directory found.")
        return
        
    novels = []
    
    for folder in sorted(os.listdir(NOVELS_DIR)):
        folder_path = os.path.join(NOVELS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
            
        match = re.match(r"^(n[a-z0-9]+)_(.+)$", folder)
        if not match:
            ncode = folder
            novel_title = folder
        else:
            ncode = match.group(1)
            novel_title = match.group(2)
            
        novels.append((novel_title, ncode, folder))
        
        # Scan raw/ for chapters
        raw_dir = os.path.join(folder_path, "raw")
        simplified_dir = os.path.join(folder_path, "simplified")
        
        chapters = []
        if os.path.exists(raw_dir):
            for file in os.listdir(raw_dir):
                if file.endswith(".md"):
                    ch_match = re.match(r"^(\d+)\.md$", file)
                    if ch_match:
                        ch_num = int(ch_match.group(1))
                        raw_path = os.path.join(raw_dir, file)
                        ch_title = parse_chapter_title(raw_path)
                        
                        has_simplified = os.path.exists(os.path.join(simplified_dir, file))
                        chapters.append((ch_num, file, ch_title, has_simplified))
                        
        chapters.sort(key=lambda x: x[0])
        
        # Write per-novel README
        novel_readme_path = os.path.join(folder_path, "README.md")
        url = f"https://ncode.syosetu.com/{ncode}/"
        
        with open(novel_readme_path, "w", encoding="utf-8") as f:
            f.write(f"# {novel_title} ({ncode})\n\n")
            f.write(f"- Source: [Syosetu URL]({url})\n\n")
            f.write("## Chapters\n\n")
            f.write("| Chapter | Raw Text | Simplified Text | Title |\n")
            f.write("| --- | --- | --- | --- |\n")
            for ch_num, filename, title, has_simp in chapters:
                raw_link = f"./raw/{filename}"
                simplified_link = f"./simplified/{filename}" if has_simp else "N/A"
                f.write(f"| Chapter {ch_num} | [Raw]({raw_link}) | [Simplified]({simplified_link}) | {title} |\n")
                
        print(f"Generated README for {novel_title}")
        
    # Write master README
    with open(ROOT_README, "w", encoding="utf-8") as f:
        f.write("# My Personal Novel Library\n\n")
        f.write("Table of contents of novels currently downloaded and simplified.\n\n")
        f.write("## Novels\n")
        for novel_title, ncode, folder in novels:
            f.write(f"- [{novel_title} ({ncode})](./novels/{folder}/README.md)\n")
            
    print("Generated master README")

if __name__ == "__main__":
    init_readmes()
