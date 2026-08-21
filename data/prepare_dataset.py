"""Normalize local public datasets into a binary ad hominem corpus."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

POSITIVE_FIELDS = ("insult", "identity_hate", "ad_hominem", "ad hominem", "fallacy")
TEXT_FIELDS = ("text", "comment_text", "comment", "sentence", "argument", "body", "source_article")


def _value(row: dict[str, str], names: tuple[str, ...]) -> str:
    lowered = {str(k).strip().lower(): (v or "") for k, v in row.items()}
    for name in names:
        if lowered.get(name, "").strip():
            return lowered[name].strip()
    return ""


def _label(row: dict[str, str], source: str) -> int | None:
    lowered = {str(k).strip().lower(): (v or "").strip().lower() for k, v in row.items()}
    if "logical_fallacies" in lowered:
        return int("ad hominem" in lowered["logical_fallacies"].replace("_", " "))
    if "cmv" in source.lower():
        return 0
    if "jigsaw" in source.lower():
        candidate_fields = [lowered.get(field) for field in ("insult", "identity_hate") if field in lowered]
        if candidate_fields:
            return int(any(value in {"1", "true", "yes"} for value in candidate_fields))
        return None
    for field in POSITIVE_FIELDS:
        value = lowered.get(field, "")
        if value in {"1", "true", "yes", "ad hominem", "ad_hominem"}:
            return 1
    if "fallacy" in lowered and "ad hominem" in lowered["fallacy"]:
        return 1
    if any(lowered.get(field) in {"1", "true", "yes"} for field in ("toxic", "label")):
        return 1
    return 0


def load_rows(input_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(input_dir.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for raw in csv.DictReader(handle):
                text = _value(raw, TEXT_FIELDS)
                label = _label(raw, path.stem)
                if text and label is not None:
                    rows.append({"text": text, "label": label, "source": path.stem})
    return rows


def prepare(rows: list[dict[str, object]], seed: int = 42) -> dict[str, list[dict[str, object]]]:
    unique: dict[str, dict[str, object]] = {}
    for row in rows:
        key = hashlib.sha256(str(row["text"]).casefold().encode()).hexdigest()
        unique.setdefault(key, row)
    grouped = {0: [], 1: []}
    for row in unique.values():
        grouped[int(row["label"])].append(row)
    size = min(len(grouped[0]), len(grouped[1]))
    if not size:
        raise ValueError("Need at least one example in each class")
    rng = random.Random(seed)
    for group in grouped.values():
        rng.shuffle(group)
    splits = {"train": [], "val": [], "test": []}
    for label in (0, 1):
        group = grouped[label][:size]
        train_end = max(1, int(len(group) * 0.8))
        val_size = max(1, int(len(group) * 0.1)) if len(group) >= 3 else 0
        val_end = min(len(group), train_end + val_size)
        splits["train"].extend(group[:train_end])
        splits["val"].extend(group[train_end:val_end])
        splits["test"].extend(group[val_end:])
    for split in splits.values():
        rng.shuffle(split)
    return splits


def write_splits(splits: dict[str, list[dict[str, object]]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in splits.items():
        with (output_dir / f"{name}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["text", "label", "source"])
            writer.writeheader()
            writer.writerows(rows)


def write_report(rows: list[dict[str, object]], splits: dict[str, list[dict[str, object]]], output_dir: Path) -> None:
    counts = {str(label): sum(int(row["label"]) == label for row in rows) for label in (0, 1)}
    split_counts = {
        name: {str(label): sum(int(row["label"]) == label for row in split) for label in (0, 1)}
        for name, split in splits.items()
    }
    report = {"total_rows": len(rows), "class_counts": counts, "splits": split_counts}
    (output_dir / "balance_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    rows = load_rows(args.input_dir)
    splits = prepare(rows)
    write_splits(splits, args.output_dir)
    write_report(rows, splits, args.output_dir)
    print(f"Wrote normalized data to {args.output_dir}")


if __name__ == "__main__":
    main()
