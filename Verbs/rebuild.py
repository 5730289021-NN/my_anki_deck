#!/usr/bin/env python3
"""Rebuild VerbAll.txt and the Tiers/ deck files from the source data.

VerbG1/G2/G3 are the sources of truth (grouped by conjugation type).
VerbAll.txt is the same 125 verbs re-ordered by frequency of use, so
instead of storing it as a fourth duplicate file, verb_index.tsv records
where each row of VerbAll came from: (source_file, source_row).

Tiers/VerbTier1_Essential.txt / VerbTier2_Common.txt / VerbTier3_LessCommon.txt
are in turn just a 42/42/41 slice of VerbAll.txt (still frequency-ordered),
so they're also derived here instead of being stored separately.

verb_index.tsv columns:
    order        - 1-indexed position in VerbAll.txt
    source_file  - VerbG1.txt / VerbG2.txt / VerbG3.txt
    source_row   - 1-indexed row within that source's data rows
    front        - kanji front, kept for human readability / sanity checks
    meaning      - meaning, kept for human readability / sanity checks

Usage:
    python3 rebuild.py
"""

import os

VERBS_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(VERBS_DIR, "verb_index.tsv")
OUTPUT_PATH = os.path.join(VERBS_DIR, "VerbAll.txt")
TIERS_DIR = os.path.join(VERBS_DIR, "Tiers")

HEADER = ["#separator:tab", "#html:true", "#columns:Front\tBack"]

# (output filename, start, end) -- start/end are 1-indexed, inclusive, into VerbAll's rows
TIER_PLAN = [
    ("VerbTier1_Essential.txt", 1, 42),
    ("VerbTier2_Common.txt", 43, 84),
    ("VerbTier3_LessCommon.txt", 85, 125),
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
        header = f.readline()  # skip column header row
        for line in f:
            raw = line.rstrip("\n")
            if not raw.strip():
                continue
            order, source_file, source_row, front, meaning = raw.split("\t", 4)
            entries.append((int(order), source_file, int(source_row), front, meaning))
    entries.sort(key=lambda e: e[0])
    return entries


def rebuild_verb_all():
    index = load_index(INDEX_PATH)

    source_cache = {}
    out_rows = []
    for order, source_file, source_row, front, meaning in index:
        if source_file not in source_cache:
            source_cache[source_file] = data_rows(os.path.join(VERBS_DIR, source_file))
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


def split_tiers(verb_all_rows):
    os.makedirs(TIERS_DIR, exist_ok=True)
    expected_total = TIER_PLAN[-1][2]
    if len(verb_all_rows) != expected_total:
        raise ValueError(
            f"VerbAll has {len(verb_all_rows)} entries, expected {expected_total}. "
            "Update TIER_PLAN's ranges before splitting."
        )
    for out_name, start, end in TIER_PLAN:
        chunk = verb_all_rows[start - 1:end]
        out_path = os.path.join(TIERS_DIR, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(HEADER + chunk) + "\n")
        print(f"{out_name}: {len(chunk)} entries (rows {start}-{end} of VerbAll.txt)")


def main():
    verb_all_rows = rebuild_verb_all()
    split_tiers(verb_all_rows)


if __name__ == "__main__":
    main()
