#!/usr/bin/env python3
"""Rebuild Composite.txt from all the sub-deck sources.

This is the top-level rebuild: it first calls each category's own rebuild
script to refresh its derived files (VerbAll/AdjectiveAll + their Tiers,
and the Kanji Tiers), then merges the current state of every tier/standalone
file into one Composite.txt with Front/Back/Tags/Deck columns, so Anki can
route each card into the right sub-deck on import.

Usage:
    python3 rebuild.py
"""

import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Sub-rebuild scripts to run first, so their derived files are fresh.
SUB_REBUILDS = [
    os.path.join(ROOT_DIR, "Verbs", "rebuild.py"),
    os.path.join(ROOT_DIR, "Adjectives", "rebuild.py"),
    os.path.join(ROOT_DIR, "Kanji", "split_tiers.py"),
]

# (relative path from ROOT_DIR, deck path, tag)
SOURCES = [
    ("Verbs/Tiers/VerbTier1_Essential.txt", "Japanese::Verbs::Tier1_Essential", "verb"),
    ("Verbs/Tiers/VerbTier2_Common.txt", "Japanese::Verbs::Tier2_Common", "verb"),
    ("Verbs/Tiers/VerbTier3_LessCommon.txt", "Japanese::Verbs::Tier3_LessCommon", "verb"),
    ("Adjectives/Tiers/AdjectiveTier1_Essential.txt", "Japanese::Adjectives::Tier1_Essential", "adjective"),
    ("Adjectives/Tiers/AdjectiveTier2_Common.txt", "Japanese::Adjectives::Tier2_Common", "adjective"),
    ("Adjectives/Tiers/AdjectiveTier3_LessCommon.txt", "Japanese::Adjectives::Tier3_LessCommon", "adjective"),
    ("Kanji/Tiers/N5Tier1.txt", "Japanese::Kanji::N5::Tier1", "kanji-n5"),
    ("Kanji/Tiers/N5Tier2.txt", "Japanese::Kanji::N5::Tier2", "kanji-n5"),
    ("Kanji/Tiers/N4Tier1.txt", "Japanese::Kanji::N4::Tier1", "kanji-n4"),
    ("Kanji/Tiers/N4Tier2.txt", "Japanese::Kanji::N4::Tier2", "kanji-n4"),
    ("Kanji/Tiers/N4Tier3.txt", "Japanese::Kanji::N4::Tier3", "kanji-n4"),
    ("Kanji/Tiers/N4Tier4.txt", "Japanese::Kanji::N4::Tier4", "kanji-n4"),
    ("Nouns/Family.txt", "Japanese::Vocabulary::Family", "vocab-family"),
    ("Direction.txt", "Japanese::Vocabulary::Direction", "vocab-direction"),
    ("Nouns/Place.txt", "Japanese::Vocabulary::Places", "vocab-places"),
    ("Class Lessons.txt", "Japanese::Class-Lessons", "class-lessons"),
]

OUTPUT_PATH = os.path.join(ROOT_DIR, "Composite.txt")
# Columns are Front, Back, Tags, Deck (in that order). The "#tags column" and
# "#deck column" directives are what actually make Anki auto-route each row
# into its tags/deck on import (requires Anki 2.1.54+) -- just naming a
# column "Deck" in #columns is not enough, Anki won't infer that on its own.
HEADER = [
    "#separator:tab",
    "#html:true",
    "#columns:Front\tBack\tTags\tDeck",
    "#tags column:3",
    "#deck column:4",
]


def run_sub_rebuilds():
    for script in SUB_REBUILDS:
        print(f"--- running {os.path.relpath(script, ROOT_DIR)} ---", flush=True)
        subprocess.run([sys.executable, script], check=True, cwd=os.path.dirname(script))


def data_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw.strip() or raw.startswith("#"):
                continue
            rows.append(raw)
    return rows


def build_composite():
    out_lines = list(HEADER)
    total = 0
    for rel_path, deck, tag in SOURCES:
        full_path = os.path.join(ROOT_DIR, rel_path)
        rows = data_rows(full_path)
        for raw in rows:
            front, back = raw.split("\t", 1)
            out_lines.append(f"{front}\t{back}\t{tag}\t{deck}")
        print(f"{rel_path}: {len(rows)} -> {deck}")
        total += len(rows)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")

    print(f"TOTAL cards: {total}")
    print(f"Wrote {OUTPUT_PATH}")


def main():
    run_sub_rebuilds()
    build_composite()


if __name__ == "__main__":
    main()
