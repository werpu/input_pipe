#!/usr/bin/env bash
set -e
mkdir -p dist_py
python3 -m venv .venv
source .venv/bin/activate
pip install pynput pyinstaller
pyinstaller -s -n key_server --onefile --distpath ./dist_py/ key_server.py
pyinstaller -s -n key_client --onefile --distpath ./dist_py/ key_client.py
deactivate
echo "built dist_py/key_server and dist_py/key_client (Python)"
