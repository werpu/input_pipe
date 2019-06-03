#!/usr/bin/env bash
#cd src/test/python
export PYTHONPATH=src/test/python:src/main/python:$PYTHONPATH
pipenv  run "cd src/test/python && python ./TestSuite.py"