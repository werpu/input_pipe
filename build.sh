#!/usr/bin/env bash
cd src/main/python
export PIPENV_IGNORE_VIRTUALENVS=1
pipenv run pyinstaller -s  -n input_pipe --onefile --distpath ../../../dist/ ./input_pipe.py
