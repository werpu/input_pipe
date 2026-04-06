#!/usr/bin/env bash
set -e
mkdir -p dist
python3 -m venv .venv
source .venv/bin/activate
pip install evdev pyinstaller
pyinstaller -s -n key_server --onefile --distpath ./dist/ key_server.py
pyinstaller -s -n key_client --onefile --distpath ./dist/ key_client.py
deactivate
echo "built dist/key_server and dist/key_client (Python)"
