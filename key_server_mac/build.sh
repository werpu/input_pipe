#!/usr/bin/env bash
pip install pynput pyinstaller
pyinstaller -s -n key_server --onefile --distpath ./dist/ key_server.py
pyinstaller -s -n key_client --onefile --distpath ./dist/ key_client.py
