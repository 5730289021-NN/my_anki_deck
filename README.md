# Japanese Anki Decks

Personal study decks for Anki, built as tab-separated `.txt` files ready for
Anki's text import (File → Import → map columns → Basic note type).

## Quick start

```bash
cd "Personal Study/Anki"
python3 rebuild.py
```

This regenerates every derived file and produces one `Composite.txt`.

Then in Anki:

1. **File → Import...** and select `Composite.txt`.
2. Set **Note type** to `Basic`.
3. Set **Field separator** to `Tab`.
4. Map the columns: `Front` → Front, `Back` → Back, `Tags` → Tags, `Deck` → Deck.
5. Import — cards land pre-sorted into decks like `Japanese::Kanji::N5::Tier1`.

Requires Anki 2.1.50+ for the per-column Deck mapping (see
[Card format](#card-format) below). Study Tier 1 of any category first —
everything is ordered from most to least commonly used.

## Folder structure

```
Verbs/
  VerbG1.txt, VerbG2.txt, VerbG3.txt   source of truth (godan / ichidan / irregular)
  verb_index.tsv                       maps VerbAll's frequency order back to (source file, row)
  rebuild.py                           regenerates VerbAll.txt + Tiers/
  VerbAll.txt                          generated: all 125 verbs, sorted by frequency of use
  Tiers/VerbTier1_Essential.txt        generated: 42/42/41 split of VerbAll.txt
  Tiers/VerbTier2_Common.txt
  Tiers/VerbTier3_LessCommon.txt

Adjectives/
  Adjective-i.txt, Adjective-na.txt    source of truth (i-adjectives / na-adjectives)
  adjective_index.tsv                  maps AdjectiveAll's frequency order back to (source file, row)
  rebuild.py                           regenerates AdjectiveAll.txt + Tiers/
  AdjectiveAll.txt                     generated: all 123 adjectives, sorted by frequency of use
  Tiers/AdjectiveTier1_Essential.txt   generated: 41/41/41 split of AdjectiveAll.txt
  Tiers/AdjectiveTier2_Common.txt
  Tiers/AdjectiveTier3_LessCommon.txt

Kanji/
  N5.txt, N4.txt                       source of truth (80 / 170 kanji, already frequency-ordered
                                        per Kanshudo's JLPT collection)
  split_tiers.py                       regenerates Tiers/ from N5.txt / N4.txt
  Tiers/N5Tier1.txt, N5Tier2.txt        generated: 40/40 split of N5.txt
  Tiers/N4Tier1-4.txt                   generated: 43/43/42/42 split of N4.txt

Nouns/
  Family.txt                           people/family vocabulary
  Place.txt                            places/shops vocabulary

Direction.txt                          direction/location vocabulary
Class Lessons.txt                      vocab + grammar patterns pulled from study-log notes

Composite.txt                          generated: every Tier file + the standalone decks above,
                                        merged into one file with Tags/Deck columns
rebuild.py                             top-level: reruns every sub-rebuild, then rebuilds Composite.txt
```

## Source of truth vs. generated files

To avoid storing the same vocabulary multiple times, only these files are
hand-maintained:

- `Verbs/VerbG1.txt`, `VerbG2.txt`, `VerbG3.txt`
- `Adjectives/Adjective-i.txt`, `Adjective-na.txt`
- `Kanji/N5.txt`, `Kanji/N4.txt`
- `Nouns/Family.txt`, `Nouns/Place.txt`
- `Direction.txt`
- `Class Lessons.txt`

Everything else (`VerbAll.txt`, `AdjectiveAll.txt`, every `Tiers/` folder,
and `Composite.txt`) is derived from those and is **not tracked in git**
(see `.gitignore`) — regenerate it any time with:

```bash
python3 rebuild.py
```

run from this folder. That single command:

1. Runs `Verbs/rebuild.py` — rebuilds `VerbAll.txt` from `VerbG1/G2/G3.txt` +
   `verb_index.tsv`, then splits it into `Verbs/Tiers/`.
2. Runs `Adjectives/rebuild.py` — same idea for `AdjectiveAll.txt` and
   `Adjectives/Tiers/`.
3. Runs `Kanji/split_tiers.py` — splits `N5.txt`/`N4.txt` into `Kanji/Tiers/`.
4. Merges every `Tiers/` file plus the standalone decks into `Composite.txt`.

If you edit a source file directly (e.g. fix a typo in `VerbG2.txt`), just
rerun `rebuild.py` — the `*_index.tsv` files check that the front field at
each indexed row still matches, and will raise an error instead of silently
producing a wrong deck if the source has changed shape (rows added/removed/
reordered).

## Card format

- Most decks use `#html:true` and put furigana on the front word as
  `<ruby>word<rt>reading</rt></ruby>`, with the reading dropped from the
  back (no point showing it twice).
- The verb and adjective source files (`VerbG*.txt`, `Adjective-*.txt`) put
  each conjugated form on its own line (`<br>`-separated) instead of comma
  separated, so the back of the card reads as a clean list.
- `Composite.txt` adds two extra columns, `Tags` and `Deck`, so importing it
  once routes every card into its correct sub-deck (e.g.
  `Japanese::Kanji::N4::Tier2`) instead of dumping everything into one deck.
  This needs a reasonably recent Anki (2.1.50+) to map a column to "Deck"
  during import — older Anki will just import everything into whichever
  single deck you pick.

## Frequency ordering

`VerbAll.txt`, `AdjectiveAll.txt`, and the Kanji `N5.txt`/`N4.txt` lists are
all ordered from most to least commonly used, so Tier 1 in any deck is
always the highest-value subset to study first. The Kanji ordering comes
straight from Kanshudo's JLPT kanji collection (which states it lists kanji
by frequency of use); the verb and adjective ordering is my own best-effort
judgment based on general everyday usage, not a corpus measurement — treat
the exact rank of any single word as approximate, though the overall
tiering should be reliable.
