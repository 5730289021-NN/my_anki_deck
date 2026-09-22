#!/usr/bin/env python3
"""Rebuild AdjectiveAll.txt and the Tiers/ deck files from the source data.

Adjective-i.txt (i-adjectives) and Adjective-na.txt (na-adjectives) are the
sources of truth. AdjectiveAll.txt is the same 123 adjectives re-ordered by
frequency of use, so instead of storing it as a third duplicate file,
adjective_index.tsv records where each row of AdjectiveAll came from:
(source_file, source_row).

Tiers/AdjectiveTier1_Essential.txt / AdjectiveTier2_Common.txt /
AdjectiveTier3_LessCommon.txt are in turn just a 41/41/41 slice of
AdjectiveAll.txt (still frequency-ordered), so they're also derived here
instead of being stored separately.

adjective_index.tsv columns:
    order        - 1-indexed position in AdjectiveAll.txt
    source_file  - Adjective-i.txt / Adjective-na.txt
    source_row   - 1-indexed row within that source's data rows
    front        - front field, kept for human readability / sanity checks
    meaning      - meaning, kept for human readability / sanity checks

Usage:
    python3 rebuild.py
"""

import os

ADJECTIVES_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(ADJECTIVES_DIR, "adjective_index.tsv")
OUTPUT_PATH = os.path.join(ADJECTIVES_DIR, "AdjectiveAll.txt")
TIERS_DIR = os.path.join(ADJECTIVES_DIR, "Tiers")

HEADER = ["#separator:tab", "#html:true", "#columns:Front\tBack"]

# (output filename, start, end) -- start/end are 1-indexed, inclusive, into AdjectiveAll's rows
TIER_PLAN = [
    ("AdjectiveTier1_Essential.txt", 1, 41),
    ("AdjectiveTier2_Common.txt", 42, 82),
    ("AdjectiveTier3_LessCommon.txt", 83, 123),
]


def data_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw.strip() or raw.startswith("#"):
                continue
            rows.append(raw)
    return rows


def load_index(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        f.readline()  # skip column header row
        for line in f:
            raw = line.rstrip("\n")
            if not raw.strip():
                continue
            order, source_file, source_row, front, meaning = raw.split("\t", 4)
            entries.append((int(order), source_file, int(source_row), front, meaning))
    entries.sort(key=lambda e: e[0])
    return entries


def rebuild_adjective_all():
    index = load_index(INDEX_PATH)

    source_cache = {}
    out_rows = []
    for order, source_file, source_row, front, meaning in index:
        if source_file not in source_cache:
            source_cache[source_file] = data_rows(os.path.join(ADJECTIVES_DIR, source_file))
        rows = source_cache[source_file]
        raw = rows[source_row - 1]
        raw_front = raw.split("\t", 1)[0]
        if raw_front != front:
            raise ValueError(
                f"Index mismatch at order {order}: expected front '{front}' from "
                f"{source_file} row {source_row}, but found '{raw_front}'. "
                "The source file may have changed since the index was built."
            )
        out_rows.append(raw)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(HEADER + out_rows) + "\n")

    print(f"Reconstructed {OUTPUT_PATH} with {len(out_rows)} entries.")
    return out_rows


def split_tiers(adjective_all_rows):
    os.makedirs(TIERS_DIR, exist_ok=True)
    expected_total = TIER_PLAN[-1][2]
    if len(adjective_all_rows) != expected_total:
        raise ValueError(
            f"AdjectiveAll has {len(adjective_all_rows)} entries, expected {expected_total}. "
            "Update TIER_PLAN's ranges before splitting."
        )
    for out_name, start, end in TIER_PLAN:
        chunk = adjective_all_rows[start - 1:end]
        out_path = os.path.join(TIERS_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(HEADER + chunk) + "\n")
        print(f"{out_name}: {len(chunk)} entries (rows {start}-{end} of AdjectiveAll.txt)")


def main():
    adjective_all_rows = rebuild_adjective_all()
    split_tiers(adjective_all_rows)


if __name__ == "__main__":
    main()
