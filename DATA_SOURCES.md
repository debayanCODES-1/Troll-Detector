# Data Sources

The raw files are downloaded locally and are excluded from Git. Keep the upstream license and citation alongside any redistribution.

| Source | Local command | Use |
| --- | --- | --- |
| `tasksource/logical-fallacy` | `python -m data.download_public` | `source_article` is text; `ad hominem` in `logical_fallacies` is label 1 |

After downloading, run `python -m data.prepare_dataset`. The generated `data/processed/balance_report.json` records the class counts and split counts used for training. Do not represent the public corpus as human-labeled civil disagreement data; add reviewed rows through `data/manual_labeling_template.csv` only after a human has assigned each label.