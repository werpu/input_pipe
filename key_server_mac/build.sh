#!/usr/bin/env bash
# Builds both Go client and Python server+client.
# Use build_go.sh or build_python.sh to build individually.
set -e
bash build_go.sh
bash build_python.sh
