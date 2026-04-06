#!/usr/bin/env bash
set -e
mkdir -p dist
go build -o dist/key_client ./client/
go build -o dist/key_server ./server/
echo "built dist/key_client and dist/key_server (Go)"
