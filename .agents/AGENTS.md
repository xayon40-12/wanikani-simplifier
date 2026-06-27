# Antigravity Rules for WaniKani Japanese Translator

This file defines rules and workflows for AI agents working in this repository.

## Novel Simplification Workflow (Path A)

When the user asks to "rewrite a novel chapter using only known kanji", follow this exact iterative verification procedure:

1. **Setup and Known Kanji Fetch**:
   - Run `./fetch_kanji.py` to ensure the known kanji list (`kanji_list.txt`) is updated with the user's latest WaniKani progress (SRS stage 3+ / Apprentice 3+).
   - Read the known kanji list from `kanji_list.txt`.

2. **Source Reading**:
   - Locate the raw downloaded chapter file at `novels/{ncode}_{title}/raw/{chapter}.txt`.
   - *Note*: If you only have the `{ncode}`, search for directories matching `novels/{ncode}_*` to find the correct folder path.
   - If not present, download it first by running `./fetch_syosetu.py {ncode} {chapter}`.

3. **Iterative Rewriting & Verification Loop**:
   - Draft a rewritten version of the text.
   - **Constraint**: You must *only* use kanji characters present in `kanji_list.txt`.
   - **Constraint**: Do not simply replace unknown kanji with Hiragana unless the word is typically/normally written in Hiragana. Instead, rewrite the sentences naturally, using vocabulary and synonyms that consist of known kanji (e.g. rewrite `叫び声` to `大きな声`, or `一瞬` to `短い時間`). Maintain the original grammar, meaning, and dramatic tone as closely as possible.
   - Write the draft to a temporary file, e.g., `novels/{ncode}_{title}/simplified/{chapter}_draft.txt`.
   - Run `./find_unknown_kanji.py novels/{ncode}_{title}/simplified/{chapter}_draft.txt`.
   - Analyze the checker's output:
     - If the checker outputs **0 unknown kanji**, the draft is approved. Proceed to Step 4.
     - If the checker finds unknown kanji, extract their locations and the kanji characters. Rewrite the specific lines in the draft to eliminate them, overwrite the draft file, and re-run the checker.
     - Repeat this verification loop until the validator returns no unknown kanji.

4. **Saving the Final Chapter**:
   - Move or save the verified clean text to `novels/{ncode}_{title}/simplified/{chapter}.txt`.
   - Remove any temporary draft files.
   - Report the completion to the user, highlighting any major phrasing compromises made to fit their vocabulary.
