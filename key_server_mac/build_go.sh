#!/usr/bin/env bash
set -e
mkdir -p dist_go
go build -o dist_go/key_client ./client/
go build -o dist_go/key_server ./server/
echo "built dist_go/key_client and dist_go/key_server (Go)"
