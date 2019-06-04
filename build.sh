#!/usr/bin/env bash
cd src/main/python
export PIPENV_IGNORE_VIRTUALENVS=1
pipenv run pyinstaller --onefile --distpath ../../../dist/ ./input_pipe.py
