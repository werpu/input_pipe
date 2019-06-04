#!/usr/bin/env bash
export PIPENV_IGNORE_VIRTUALENVS=1
cd src/main/python
pipenv run python input_pipe.py -c ../resources/devices.yaml

