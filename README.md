# CivilDialog v2

CivilDialog is a Chrome Manifest V3 extension for YouTube, X replies, and Instagram comments. Before submission it runs two independent checks: a client-configured word filter and a locally hosted ad hominem classifier. No comment text is sent to a third-party API. The core classifier judges whether wording attacks a person rather than whether an opinion is true or acceptable.

## Architecture

`data/download_public.py` downloads the licensed `tasksource/logical-fallacy` source into `data/raw/`; `data/prepare_dataset.py` normalizes it into binary `text,label,source` CSV files and writes `data/processed/balance_report.json`. The server uses an external OpenAI-compatible AI API for fallacy detection and explanations, while the word filter remains local.

`server/main.py` serves FastAPI on `127.0.0.1:8787`. `/check/wordfilter` is pure local JSON blocklist matching, `/check/fallacy` and `/explain` call the configured AI provider, and both fall back safely when the provider is unavailable. The extension's service worker remains the only network client and only targets that loopback address.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export AI_API_KEY="your-api-key"
export AI_API_URL="https://api.groq.com/openai/v1/chat/completions"
export AI_MODEL="llama-3.1-8b-instant"
python -m uvicorn server.main:app --host 127.0.0.1 --port 8787
```

The default provider is Groq's OpenAI-compatible API. Create a free key at [console.groq.com](https://console.groq.com/), then set `AI_API_KEY`. Set `AI_API_URL` and `AI_MODEL` for another compatible provider. Keep the key on the server; never put it in the extension.

On Windows, run `run_server.bat` after installing requirements in `.venv`. Load `extension/` from `chrome://extensions` with Developer mode enabled. The popup stores each toggle in `chrome.storage.sync` and reports local server liveness.

## Deployment

For a repeatable local deployment, build and start the inference service with Docker:

```bash
export AI_API_KEY="your-api-key"
export AI_API_URL="https://api.groq.com/openai/v1/chat/completions"
export AI_MODEL="llama-3.1-8b-instant"
docker compose up --build -d
curl http://127.0.0.1:8787/health
```

The compose file publishes the service only on loopback, which matches the extension's configured API target. It passes `AI_API_KEY`, `AI_API_URL`, and `AI_MODEL` through the environment without baking credentials into the image. Stop it with `docker compose down`.

## Data and model

Public datasets and human-labeled examples are intentionally not bundled. See [DATA_SOURCES.md](DATA_SOURCES.md) for provenance and [data/README.md](data/README.md) for the manual labeling scaffold. Add a few hundred human-reviewed civil-disagreement examples before relying on the extension; the downloaded fallacy corpus is not a substitute for those labels. Threshold selection favors positive-class precision because blocking clean comments harms trust.

## Limitations

Platform DOMs change. X is limited to replies and Instagram supports textarea/contenteditable selectors that may need maintenance. The API client retries one transient failure and returns a conservative fallback if the provider is unavailable. See [extension/tests/README.md](extension/tests/README.md) for browser checks.
