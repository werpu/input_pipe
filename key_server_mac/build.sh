#!/usr/bin/env bash
python3 -m venv .venv
source .venv/bin/activate
pip install pynput pyinstaller
pyinstaller -s -n key_server --onefile --distpath ./dist/ key_server.py
pyinstaller -s -n key_client --onefile --distpath ./dist/ key_client.py
deactivate
