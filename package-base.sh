#!/usr/bin/env bash
# PicoWDesk – Base Installation
# Minimal desktop only (no apps).

set -e
DEPLOY_DIR="deploy"

echo "🧹 Clearing $DEPLOY_DIR…"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

echo "📦 Copying base files…"
cp main.py "$DEPLOY_DIR/"
cp index.html "$DEPLOY_DIR/"
cp config.json "$DEPLOY_DIR/"
cp favicon.ico "$DEPLOY_DIR/"

echo "📄 Adding generic installation guide…"
cp docs/INSTALL.md "$DEPLOY_DIR/"

echo "✅ Base package ready in $DEPLOY_DIR"