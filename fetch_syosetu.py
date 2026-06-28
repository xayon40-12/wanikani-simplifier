#!/usr/bin/env python3
import sys
import os
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser

class SyosetuParser(HTMLParser):
    def __init__(self, ncode, keep_ruby=False):
        super().__init__()
        self.ncode = ncode
        self.keep_ruby = keep_ruby
        self.in_title = False
        self.in_novel_text = False
        self.in_p = False
        self.in_rt = False
        self.in_novel_title_link = False
        
        self.title = ""
        self.novel_title = ""
        self.temp_novel_title = ""
        self.paragraphs = []
        self.current_paragraph = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_class = attrs_dict.get("class", "")
        tag_id = attrs_dict.get("id", "")
        href = attrs_dict.get("href", "")
        
        # Match exact novel URL pattern: e.g. /n2267be/ or https://ncode.syosetu.com/n2267be/
        is_novel_link = False
        if tag == "a" and href:
            pattern = r'^(https?://[^/]+)?/' + re.escape(self.ncode) + r'/?$'
            if re.match(pattern, href):
                is_novel_link = True

        if is_novel_link:
            if "c-pager__item" not in tag_class and not self.novel_title:
                self.in_novel_title_link = True
                self.temp_novel_title = ""
        elif tag == "p" and tag_class == "novel_title" and not self.novel_title:
            self.in_novel_title_link = True
            self.temp_novel_title = ""
            
        # Chapter title
        elif tag == "h1" and ("p-novel__title" in tag_class or tag_class == "novel_subtitle"):
            self.in_title = True
        elif tag == "p" and (tag_class == "novel_subtitle"):
            self.in_title = True
            
        # Novel text container
        elif tag == "div" and ("p-novel__text" in tag_class or "novel_view" in tag_class or tag_id == "novel_honbun"):
            self.in_novel_text = True
            
        # Paragraphs
        elif tag == "p" and self.in_novel_text:
            self.in_p = True
            self.current_paragraph = ""
            
        # Ruby
        elif tag == "rt" and self.in_p:
            self.in_rt = True
            if self.keep_ruby:
                self.current_paragraph += "("

    def handle_endtag(self, tag):
        if tag in ["a", "p"] and self.in_novel_title_link:
            self.in_novel_title_link = False
            self.novel_title = self.temp_novel_title.strip()
        elif tag in ["h1", "p"] and self.in_title:
            self.in_title = False
        elif tag == "div" and self.in_novel_text:
            self.in_novel_text = False
        elif tag == "p" and self.in_p:
            self.in_p = False
            self.paragraphs.append(self.current_paragraph.strip())
        elif tag == "rt" and self.in_rt:
            self.in_rt = False
            if self.keep_ruby:
                self.current_paragraph += ")"

    def handle_data(self, data):
        if self.in_novel_title_link:
            self.temp_novel_title += data
        elif self.in_title:
            self.title += data
        elif self.in_p:
            if not self.in_rt or self.keep_ruby:
                self.current_paragraph += data

def parse_url_or_ncode(input_str):
    input_str = input_str.strip().lower()
    
    # Try to extract domain, defaults to ncode.syosetu.com
    domain = "ncode.syosetu.com"
    domain_match = re.search(r'https?://([^/]+)/', input_str)
    if domain_match:
        domain = domain_match.group(1)
        
    match = re.search(r'(n[a-z0-9]+)(?:/(\d+))?/?$', input_str)
    if match:
        ncode = match.group(1)
        chapter = match.group(2)
        return domain, ncode, chapter
        
    return domain, None, None

def sanitize_filename(name):
    # Remove characters invalid in filenames: \ / * ? : " < > |
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def download_chapter(domain, ncode, chapter=None, keep_ruby=False):
    if chapter:
        url = f"https://{domain}/{ncode}/{chapter}/"
    else:
        url = f"https://{domain}/{ncode}/"
        
    print(f"Downloading from: {url}")
    
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    req.add_header("Accept-Language", "ja,en-US;q=0.9,en;q=0.8")
    req.add_header("Cookie", "over18=yes")
    
    try:
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print("Please check if the novel code and chapter number are correct.")
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)
        
    parser = SyosetuParser(ncode, keep_ruby=keep_ruby)
    parser.feed(html_content)
    
    title = parser.title.strip() if parser.title else "Untitled"
    novel_title = parser.novel_title.strip()
    paragraphs = parser.paragraphs
    
    # Establish folder name based on novel title if found
    novel_folder_name = ncode
    if novel_title:
        sanitized_title = sanitize_filename(novel_title)
        if sanitized_title:
            # Replaces any colons or slashes that might be tricky on macOS filesystem
            novel_folder_name = f"{ncode}_{sanitized_title}"
            
    if chapter:
        output_dir = os.path.join("personal", "novels", novel_folder_name, "raw")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, f"{chapter}.md")
    else:
        output_dir = os.path.join("personal", "novels", novel_folder_name)
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, "main.md")
        
    if not paragraphs:
        print("Warning: No chapter text found. The page might be an index page or structured differently.")
        if not chapter:
            print("Since no chapter was specified, this might be the main index page.")
            
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            f.write(f"Source: {url}\n")
            f.write("-" * 40 + "\n\n")
            for para in paragraphs:
                f.write(f"{para}\n")
        print(f"Saved chapter text to: {output_filename}")
        update_readme_indices(ncode, novel_title if novel_title else ncode, novel_folder_name, chapter, title)
        return output_filename
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

def update_readme_indices(ncode, novel_title, novel_folder_name, chapter, chapter_title):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    personal_dir = os.path.join(base_dir, "personal")
    master_readme = os.path.join(personal_dir, "README.md")
    
    os.makedirs(personal_dir, exist_ok=True)
    
    # 1. Update master README
    novels_list = []
    novel_entry = f"- [{novel_title} ({ncode})](./novels/{novel_folder_name}/README.md)"
    
    if os.path.exists(master_readme):
        try:
            with open(master_readme, "r", encoding="utf-8") as f:
                content = f.read()
                novels_list = [line.strip() for line in content.split("\n") if line.strip().startswith("- [")]
        except Exception as e:
            print(f"Warning: Could not read master README: {e}")
            
    if novel_entry not in novels_list:
        novels_list.append(novel_entry)
        novels_list.sort()
        
    try:
        with open(master_readme, "w", encoding="utf-8") as f:
            f.write("# My Personal Novel Library\n\n")
            f.write("Table of contents of novels currently downloaded and simplified.\n\n")
            f.write("## Novels\n")
            for entry in novels_list:
                f.write(f"{entry}\n")
    except Exception as e:
        print(f"Warning: Could not write master README: {e}")
        
    # 2. Update novel README
    novel_dir = os.path.join(personal_dir, "novels", novel_folder_name)
    novel_readme = os.path.join(novel_dir, "README.md")
    
    os.makedirs(novel_dir, exist_ok=True)
    
    chapters_dict = {}
    
    if os.path.exists(novel_readme):
        try:
            with open(novel_readme, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r"^\|\s*Chapter\s+(\d+)\s*\|\s*\[Raw\]\((?P<raw>[^)]+)\)\s*\|\s*(?P<simp>\[Simplified\]\([^)]+\)|N/A)\s*\|\s*(?P<title>.*?)\s*\|$", line.strip())
                    if match:
                        ch_num = int(match.group(1))
                        raw_link = match.group("raw")
                        simp_link = match.group("simp")
                        title = match.group("title").strip()
                        chapters_dict[ch_num] = (raw_link, simp_link, title)
        except Exception as e:
            print(f"Warning: Could not parse novel README: {e}")
            
    if chapter:
        try:
            ch_num = int(chapter)
            raw_link = f"./raw/{chapter}.md"
            simp_file = os.path.join(novel_dir, "simplified", f"{chapter}.md")
            simp_link = f"[Simplified](./simplified/{chapter}.md)" if os.path.exists(simp_file) else "N/A"
            chapters_dict[ch_num] = (raw_link, simp_link, chapter_title)
        except ValueError:
            pass
            
    try:
        with open(novel_readme, "w", encoding="utf-8") as f:
            f.write(f"# {novel_title} ({ncode})\n\n")
            url = f"https://ncode.syosetu.com/{ncode}/"
            f.write(f"- Source: [Syosetu URL]({url})\n\n")
            f.write("## Chapters\n\n")
            f.write("| Chapter | Raw Text | Simplified Text | Title |\n")
            f.write("| --- | --- | --- | --- |\n")
            for ch_num in sorted(chapters_dict.keys()):
                raw, simp, title = chapters_dict[ch_num]
                f.write(f"| Chapter {ch_num} | [Raw]({raw}) | {simp} | {title} |\n")
    except Exception as e:
        print(f"Warning: Could not write novel README: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: ./fetch_syosetu.py <novel_url_or_ncode> [chapter_number] [--keep-ruby]")
        print("Examples:")
        print("  ./fetch_syosetu.py https://ncode.syosetu.com/n2267be/1/")
        print("  ./fetch_syosetu.py n2267be 1")
        print("  ./fetch_syosetu.py n2267be 1 --keep-ruby")
        sys.exit(1)
        
    input_arg = sys.argv[1]
    chapter_arg = None
    keep_ruby = False
    
    args = sys.argv[2:]
    if "--keep-ruby" in args:
        keep_ruby = True
        args.remove("--keep-ruby")
        
    if args:
        chapter_arg = args[0]
        
    domain, ncode, url_chapter = parse_url_or_ncode(input_arg)
    
    if not ncode:
        print(f"Error: Could not extract a valid novel code (ncode) from: {input_arg}")
        sys.exit(1)
        
    chapter = chapter_arg if chapter_arg else url_chapter
    
    download_chapter(domain, ncode, chapter, keep_ruby)

if __name__ == "__main__":
    main()
