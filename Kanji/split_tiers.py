#!/usr/bin/env python3
"""Regenerate the tier deck files from N5.txt and N4.txt.

N5.txt and N4.txt are the source of truth (already ordered by frequency
of use). This script splits them into tier decks under Tiers/ so we don't
have to keep the tiered data duplicated on disk.

Usage:
    python3 split_tiers.py
"""

import os

KANJI_DIR = os.path.dirname(os.path.abspath(__file__))
TIERS_DIR = os.path.join(KANJI_DIR, "Tiers")

HEADER = ["#separator:tab", "#html:true", "#columns:Front\tBack"]

# (source file, [(output filename, start, end)])  -- start/end are 1-indexed, inclusive
PLAN = [
    ("N5.txt", [
        ("N5Tier1.txt", 1, 40),
        ("N5Tier2.txt", 41, 80),
    ]),
    ("N4.txt", [
        ("N4Tier1.txt", 1, 43),
        ("N4Tier2.txt", 44, 86),
        ("N4Tier3.txt", 87, 128),
        ("N4Tier4.txt", 129, 170),
    ]),
]


def read_data_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw.strip() or raw.startswith("#"):
                continue
            rows.append(raw)
    return rows


def write_tier(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(HEADER + rows) + "\n")


def main():
    os.makedirs(TIERS_DIR, exist_ok=True)
    for source_name, tiers in PLAN:
        source_path = os.path.join(KANJI_DIR, source_name)
        rows = read_data_rows(source_path)
        expected_total = tiers[-1][2]
        if len(rows) != expected_total:
            raise ValueError(
                f"{source_name} has {len(rows)} entries, expected {expected_total}. "
                "Update PLAN's tier ranges before regenerating."
            )
        for out_name, start, end in tiers:
            chunk = rows[start - 1:end]
            out_path = os.path.join(TIERS_DIR, out_name)
            write_tier(out_path, chunk)
            print(f"{out_name}: {len(chunk)} entries (rows {start}-{end} of {source_name})")


if __name__ == "__main__":
    main()
