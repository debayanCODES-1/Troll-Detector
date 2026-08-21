# CivilDialog v2

CivilDialog is a Chrome Manifest V3 extension for YouTube, X replies, and Instagram comments. Before submission it runs two independent checks: a client-configured word filter and a locally hosted ad hominem classifier. No comment text is sent to a third-party API. The core classifier judges whether wording attacks a person rather than whether an opinion is true or acceptable.

## Architecture

`data/download_public.py` downloads the licensed `tasksource/logical-fallacy` source into `data/raw/`; `data/prepare_dataset.py` normalizes it into binary `text,label,source` CSV files and writes `data/processed/balance_report.json`. `train.py` fine-tunes DistilBERT with max length 128 and records validation/test metrics. Run `python export_onnx.py` after training to create `models/fallacy_classifier.onnx` and `models/tokenizer/`.

`server/main.py` serves FastAPI on `127.0.0.1:8787`. `/check/wordfilter` is pure local JSON blocklist matching, `/check/fallacy` uses ONNX Runtime when the artifact exists and a conservative development heuristic otherwise, and `/explain` is the local explainer adapter point. The extension's service worker is the only network client and only targets that loopback address.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m data.prepare_dataset --input-dir data/raw
uvicorn server.main:app --host 127.0.0.1 --port 8787
```

On Windows, run `run_server.bat` after installing requirements in `.venv`. Load `extension/` from `chrome://extensions` with Developer mode enabled. The popup stores each toggle in `chrome.storage.sync` and reports local server liveness.

## Data and model

Public datasets and human-labeled examples are intentionally not bundled. See [DATA_SOURCES.md](DATA_SOURCES.md) for provenance and [data/README.md](data/README.md) for the manual labeling scaffold. Add a few hundred human-reviewed civil-disagreement examples before relying on the extension; the downloaded fallacy corpus is not a substitute for those labels. Threshold selection favors positive-class precision because blocking clean comments harms trust.

## Limitations

Platform DOMs change. X is limited to replies and Instagram supports textarea/contenteditable selectors that may need maintenance. The explainer loads a compatible local Phi/Llama ONNX Runtime GenAI directory from `CIVILDIALOG_EXPLAINER_MODEL` and reports an unavailable response until that model is installed. See [extension/tests/README.md](extension/tests/README.md) for browser checks.
