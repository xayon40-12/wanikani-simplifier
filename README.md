# WaniKani Japanese Novel Simplifier

A utility toolset to help Japanese learners read web novels from **小説家になろう (Syosetu.com)**. It automatically compares novel chapters against your current WaniKani progress and helps you rewrite them to only use kanji characters you already know (at SRS stage **Apprentice 3 or higher**).

This project has **zero external dependencies** and runs out-of-the-box on standard Python 3.

---

## Folder Structure

```text
├── .agents/
│   └── AGENTS.md            # Automation rules for AI assistants
├── personal/                # Personal data folder (Git-ignored in main repo)
│   ├── configs/             # Personal custom kanji lists
│   │   ├── custom_known_kanji.txt
│   │   └── custom_mastered_kanji.txt
│   └── novels/              # Downloaded and simplified novel chapters
│       └── {ncode}_{title}/
│           ├── raw/         # Raw chapters downloaded from Syosetu
│           └── simplified/  # Rewritten chapters using only known kanji
├── .gitignore
├── README.md
├── fetch_kanji.py           # Syncs known kanji from WaniKani API
├── fetch_syosetu.py         # Downloads chapters from Syosetu.com
├── find_unknown_kanji.py    # Validates novel files and lists unknown kanji
└── token.txt                # Your WaniKani API v2 Read Token (Git-ignored)
```

---

## Setup

1. **WaniKani API Token**:
   Create a file named `token.txt` in the root of the project and paste your **WaniKani API v2 read token** into it:
   ```text
   <your-wanikani-read-token-here>
   ```
   *(Alternatively, you can set the `WANIKANI_API_TOKEN` environment variable).*

2. **Verify Python**:
   Ensure you have Python 3 installed:
   ```bash
   python3 --version
   ```

3. **Personal Folder & Private Git Setup (Optional but Recommended)**:
   All your personal configurations, raw novel chapters (copyrighted), and simplified translations are saved inside a single `personal/` folder which is ignored in the main public repository.
   To back up and sync your progress across multiple devices privately:
   * **Initialization**:
     Create the `personal/` directory and initialize it as a separate private Git repository:
     ```bash
     mkdir -p personal/configs personal/novels
     cd personal
     git init
     ```
   * **Custom lists**:
     You can place your custom kanji files inside `personal/configs/`:
     * **`personal/configs/custom_known_kanji.txt`**: Add kanji you know from outside WaniKani (one per line).
     * **`personal/configs/custom_mastered_kanji.txt`**: Add kanji you have fully mastered (one per line).
   * **Pushing to a Private Repo**:
     Set up a private repository on GitHub (or GitLab) and add it as a remote inside `personal/`:
     ```bash
     git remote add origin git@github.com:yourusername/your-private-repo.git
     git add . && git commit -m "Initial commit of my translations and configs"
     git branch -M main
     git push -u origin main
     ```

---

## How to Use (Human Workflow)

### Step 1: Download a Raw Chapter
To download a chapter from Syosetu.com, use `fetch_syosetu.py`. You can provide the full URL or just the novel code (`ncode`) and chapter number.

```bash
# Example: Download Re:Zero Chapter 1
./fetch_syosetu.py https://ncode.syosetu.com/n2267be/ 1
```
* **Output Path**: `personal/novels/n2267be_Ｒｅ：ゼロから始める異世界生活/raw/1.md`
* *Tip*: Pass the `--keep-ruby` flag if you want to keep furigana readings formatted as `漢字(かんじ)`. By default, furigana is stripped.

### Step 2: Validate Against Your Kanji List
Run the checker script `find_unknown_kanji.py` on the downloaded file. It will automatically update your known kanji list from WaniKani (saving them to `kanji_list.txt`) and scan the file.

```bash
./find_unknown_kanji.py personal/novels/n2267be_Ｒｅ：ゼロから始める異世界生活/raw/1.md
```
* **Output**: A list of all unknown kanji characters found in the text, indicating their exact line and character column numbers.

### Step 3: Rewrite and Simplify
Write your simplified chapter and save it under the `simplified/` folder.
* **Grammar, Verbs, & Common Nouns**: Rephrase sentences naturally using synonyms containing **known kanji** (e.g., rewrite `伯爵` to `身分の高い家` or `炎` to `火`). Do not simply replace unknown kanji with Hiragana, as it makes vocabulary hard to parse.
* **Proper Nouns & Names**: If you want to keep proper names (like people's names, e.g., `八鍵`, or place names containing unknown kanji) recognizable, keep their original kanji and wrap them in **Katakana ruby tags** (e.g., `<ruby>八鍵<rt>ヤカギ</rt></ruby>`).

Verify the rewritten file:
```bash
./find_unknown_kanji.py personal/novels/n2267be_Ｒｅ：ゼロから始める異世界生活/simplified/1.md
```
Repeat until it reports **`0 unknown kanji`**!

---

## AI Agent Automation (Path A)

If you are using an AI coding assistant (like **Antigravity** or other agentic editors), you can automate the rewriting process completely. 

Simply open this workspace and prompt the assistant:
> *"Please rewrite chapter 1 of n2267be to only use known kanji."*

The AI assistant will automatically read the instructions in **[.agents/AGENTS.md](file:///.agents/AGENTS.md)** and execute the following loop:
1. Sync your WaniKani kanji lists (`kanji_list.txt` and `mastered_kanji.txt`).
2. Read the raw text.
3. Draft a rewrite substituting unknown kanji with known synonyms or natural phrasings.
4. Apply **Furigana (Ruby tags)** to any kanji present in the text that you have unlocked but **not yet Guru 2** (meaning it exists in `kanji_list.txt` but not in `mastered_kanji.txt`). Mastered kanji (Guru 2+) remain raw, avoiding reading clutter.
5. Run `./find_unknown_kanji.py` to identify remaining issues.
6. Correct the text and re-validate until it reaches `0 unknown kanji`.
7. Run a **self-peer-review** to restore key quotes in kana or optimize flow.
8. Save the finalized file to `personal/novels/{ncode}_{title}/simplified/{chapter}.md`.

---

## Detailed Command Reference

### `fetch_kanji.py`
Syncs kanji assignments from WaniKani at **Apprentice 3** level or above (SRS stages 3 to 9).
* To force a refresh of the cached subject dictionary:
  ```bash
  ./fetch_kanji.py --refresh
  ```
* To run using an alternative token:
  ```bash
  ./fetch_kanji.py YOUR_TOKEN
  ```

### `fetch_syosetu.py`
Downloads novel pages. Supports `novel18.syosetu.com` (Nocturne/R18) by automatically passing the age-confirmation cookie.
```bash
./fetch_syosetu.py <ncode_or_url> [chapter] [--keep-ruby]
```

### `find_unknown_kanji.py`
Validates a text file against your known kanji list (fetched from WaniKani + custom lists) and checks that all unmastered known kanji have proper Hiragana `<ruby>` tags.
```bash
./find_unknown_kanji.py <target_file>
```

### `init_library_readmes.py`
Scans your `personal/novels/` folder to generate or regenerate the wiki index files (`personal/README.md` and `personal/novels/{novel}/README.md`). Use this to rebuild the index tables manually if needed.
```bash
./init_library_readmes.py
```
