#!/usr/bin/env bash
cd src/main/python
pipenv run pyinstaller --onefile --distpath ../../../dist/ ./main.py
