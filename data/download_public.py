"""Download the licensed Hugging Face source dataset into data/raw/."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from datasets import load_dataset


def download(dataset_name: str, output_dir: Path) -> Path:
    """Materialize every available split as one CSV while retaining source metadata."""
    dataset = load_dataset(dataset_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "logical_fallacy.csv"
    rows = []
    for split_name, split in dataset.items():
        for row in split:
            item = {str(key): value for key, value in row.items()}
            item["source_split"] = split_name
            rows.append(item)
    if not rows:
        raise ValueError(f"Dataset {dataset_name!r} contains no rows")
    fields = sorted({key for row in rows for key in row})
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="tasksource/logical-fallacy")
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    print(f"Downloaded {download(args.dataset, args.output_dir)}")


if __name__ == "__main__":
    main()