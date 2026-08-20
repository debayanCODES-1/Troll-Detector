# Dataset

The preparation script expects source CSV files in `data/raw/` and writes the normalized schema `text,label,source` to `data/processed/`.

Supported source hints:

- Jigsaw Toxic Comment: `insult` and `identity_hate` rows are positive candidates; all-zero rows are clean candidates.
- CMV: rows are clean disagreement candidates (`label=0`). Review samples before training.
- Argotario/LOGIC: rows whose fallacy field contains `ad hominem` are positive candidates.

Run `python -m data.prepare_dataset --input-dir data/raw`. The script removes empty text and exact duplicates, caps each class to a balanced target, and creates deterministic 80/10/10 train/validation/test splits. Public datasets are not bundled; retain their original licenses and citations outside this repository.

A few hundred manually labeled disagreement-without-attack examples are recommended. Public toxicity data overrepresents obvious abuse and can create false positives on strong but civil opinions.
