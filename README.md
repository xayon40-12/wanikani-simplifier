# WaniKani Japanese Novel Simplifier

A utility toolset to help Japanese learners read web novels from **小説家になろう (Syosetu.com)**. It automatically compares novel chapters against your current WaniKani progress and helps you rewrite them to only use kanji characters you already know (at SRS stage **Apprentice 3 or higher**).

This project has **zero external dependencies** and runs out-of-the-box on standard Python 3.

---

## Folder Structure

```text
├── .agents/
│   └── AGENTS.md            # Automation rules for AI assistants
├── novels/                  # Local storage for downloaded novel chapters (Git-ignored)
│   └── {ncode}_{title}/
│       ├── raw/             # Raw chapters downloaded from Syosetu
│       └── simplified/      # Rewritten chapters using only known kanji
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

3. **Custom Kanji Lists (Optional)**:
   To version your personal custom kanji list without cluttering the main branch, this project checks out a separate branch (`personal-configs`) into a git-ignored subfolder `.configs/` using Git worktrees.
   * **Setup**:
     Run this command in the project root to set up the worktree:
     ```bash
     git worktree add .configs personal-configs
     ```
   * **Usage**:
     Manage your custom lists inside the `.configs/` folder:
     * **`.configs/custom_known_kanji.txt`**: Add kanji you know from outside WaniKani (one per line).
     * **`.configs/custom_mastered_kanji.txt`**: Add kanji you have fully mastered (one per line).
   * **Saving Changes**:
     To commit and push updates to your personal kanji list, change into the subfolder and commit there:
     ```bash
     cd .configs
     git add . && git commit -m "Update personal kanji list"
     git push origin personal-configs
     ```
     *(Note: If you do not use the worktree setup, the scripts will fall back to reading `custom_known_kanji.txt` in the root folder).*

---

## How to Use (Human Workflow)

### Step 1: Download a Raw Chapter
To download a chapter from Syosetu.com, use `fetch_syosetu.py`. You can provide the full URL or just the novel code (`ncode`) and chapter number.

```bash
# Example: Download Re:Zero Chapter 1
./fetch_syosetu.py https://ncode.syosetu.com/n2267be/ 1
```
* **Output Path**: `novels/n2267be_Ｒｅ：ゼロから始める異世界生活/raw/1.md`
* *Tip*: Pass the `--keep-ruby` flag if you want to keep furigana readings formatted as `漢字(かんじ)`. By default, furigana is stripped.

### Step 2: Validate Against Your Kanji List
Run the checker script `find_unknown_kanji.py` on the downloaded file. It will automatically update your known kanji list from WaniKani (saving them to `kanji_list.txt`) and scan the file.

```bash
./find_unknown_kanji.py novels/n2267be_Ｒｅ：ゼロから始める異世界生活/raw/1.md
```
* **Output**: A list of all unknown kanji characters found in the text, indicating their exact line and character column numbers.

### Step 3: Rewrite and Simplify
Write your simplified chapter and save it under the `simplified/` folder. Use synonyms, descriptive phrases, or native hiragana spellings to avoid any kanji not on your known list.

Verify the rewritten file:
```bash
./find_unknown_kanji.py novels/n2267be_Ｒｅ：ゼロから始める異世界生活/simplified/1.md
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
8. Save the finalized file to `novels/{ncode}_{title}/simplified/{chapter}.md`.

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
