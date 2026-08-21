@echo off
setlocal
cd /d %~dp0
if not exist .venv\Scripts\uvicorn.exe (
  echo Create a virtual environment and install requirements.txt first.
  exit /b 1
)
.venv\Scripts\uvicorn.exe server.main:app --host 127.0.0.1 --port 8787
