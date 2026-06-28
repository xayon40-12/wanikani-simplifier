# Antigravity Rules for WaniKani Japanese Translator

This file defines rules and workflows for AI agents working in this repository.

## Novel Simplification Workflow (Path A)

When the user asks to "rewrite a novel chapter using only known kanji", follow this exact iterative verification procedure:

1. **Setup and Known Kanji Fetch**:
   - Run `./fetch_kanji.py` to ensure the known kanji list (`kanji_list.txt`) and mastered kanji list (`mastered_kanji.txt`) are updated with the user's latest WaniKani progress.
   - Read the known kanji list from `kanji_list.txt` and mastered kanji list from `mastered_kanji.txt`. Also load custom known kanji from `custom_known_kanji.txt` (if present, checking `personal/configs/` folder first) and custom mastered kanji from `custom_mastered_kanji.txt` (if present, checking `personal/configs/` folder first), merging them into the known and mastered sets.

2. **Source Reading**:
   - Locate the raw downloaded chapter file at `personal/novels/{ncode}_{title}/raw/{chapter}.md`.
   - *Note*: If you only have the `{ncode}`, search for directories matching `personal/novels/{ncode}_*` to find the correct folder path.
   - If not present, download it first by running `./fetch_syosetu.py {ncode} {chapter}`.

3. **Iterative Rewriting & Verification Loop**:
   - Draft a rewritten version of the text.
   - **Constraint**: You must *only* use kanji characters present in `kanji_list.txt`.
   - **Constraint**: Do not simply replace unknown kanji with Hiragana unless the word is typically/normally written in Hiragana. Instead, rewrite the sentences naturally, using vocabulary and synonyms that consist of known kanji (e.g. rewrite `叫び声` to `大きな声`, or `一瞬` to `短い時間`). Maintain the original grammar, meaning, and dramatic tone as closely as possible.
   - **Proper Nouns & Names**: To keep proper names (like people's names, e.g. `八鍵` $\rightarrow$ `<ruby>八鍵<rt>ヤカギ</rt></ruby>`, or place names) recognizable, keep their original kanji and wrap them in Katakana ruby tags. All other general nouns (like `伯爵`, `貴族`), verbs, and adjectives must be simplified and rewritten using synonyms that consist of known kanji.
   - **Furigana / Ruby formatting**: Any kanji used in the simplified draft that is present in `kanji_list.txt` but **NOT** present in `mastered_kanji.txt` (meaning it is Apprentice 3, 4, or Guru 1, but not yet Guru 2) **must** be formatted with HTML ruby tags: `<ruby>漢字<rt>かんじ</rt></ruby>`. For compound words, apply the ruby tags specifically to the non-mastered kanji characters (e.g. `地<ruby>面<rt>めん</rt></ruby>`).
   - Write the draft to a temporary file, e.g., `personal/novels/{ncode}_{title}/simplified/{chapter}_draft.md`.
   - Run `./find_unknown_kanji.py personal/novels/{ncode}_{title}/simplified/{chapter}_draft.md`.
   - Analyze the checker's output:
     - If the checker outputs **0 unknown kanji**, the draft is approved. Proceed to Step 4.
     - If the checker finds unknown kanji, extract their locations and the kanji characters. Rewrite the specific lines in the draft to eliminate them, overwrite the draft file, and re-run the checker.
     - Repeat this verification loop until the validator returns no unknown kanji.

4. **Peer Review & Final Polish**:
   - Once the draft is validated (0 unknown kanji), perform a thorough self-peer review of the translation.
   - **Verification**: Check if the simplified phrasing is natural, grammatically correct, and preserves the dramatic weight of the original.
   - **Optimization**: Check if any simplified words can be restored to more accurate synonyms or exact phrases by writing them in hiragana (e.g., using `すくう` instead of `守る` for `救う` if the context warrants it) or by using newly unlocked known kanji (e.g., check for kanji that are in `kanji_list.txt` but might have been missed in initial drafts, such as `違`).
   - If any quality improvements are found, apply them to the draft immediately and run `./find_unknown_kanji.py` one final time to verify it remains at 0 unknown kanji. Do not wait for the user to prompt you for these changes; execute them proactively.

5. **Saving the Final Chapter**:
   - Move or save the verified clean text to `personal/novels/{ncode}_{title}/simplified/{chapter}.md`.
   - Remove any temporary draft files.
   - Report the completion to the user, highlighting the major phrasing choices, synonyms used, and peer-review improvements made.
