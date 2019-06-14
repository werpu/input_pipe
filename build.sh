#!/usr/bin/env bash
#cd src/main/python
#export PIPENV_IGNORE_VIRTUALENVS=1
rm ./dist/input_pipe
pipenv run pyinstaller -s  -n input_pipe --onefile --distpath ./dist/ ./src/main/python/input_pipe.py
