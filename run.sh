#!/usr/bin/env bash
export PIPENV_IGNORE_VIRTUALENVS=1
cd src/main/python
pipenv run python main.py --config ../resources/devices.yaml

