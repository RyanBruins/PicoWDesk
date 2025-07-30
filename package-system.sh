#!/usr/bin/env bash
# PicoWDesk – System Installation
# Base + system apps, with _Settings_ virtual folder.

set -e
DEPLOY_DIR="deploy"
SYS_SRC="apps/system"

echo "🧹 Clearing $DEPLOY_DIR…"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

echo "📦 Copying base files…"
cp main.py "$DEPLOY_DIR/"
cp index.html "$DEPLOY_DIR/"
cp config.json "$DEPLOY_DIR/"
cp favicon.ico "$DEPLOY_DIR/"

echo "📂 Copying system apps and prefixing for _Settings_ virtual folder…"
for f in "$SYS_SRC"/*.html; do
    [ -e "$f" ] || continue
    basename=$(basename "$f")
    case "$basename" in
        NetworkSettings.html|Restart.html|Info.html)
            cp "$f" "$DEPLOY_DIR/_Settings_$basename"
            ;;
        *)
            cp "$f" "$DEPLOY_DIR/$basename"
            ;;
    esac
done
cp "$SYS_SRC"/*.ico "$DEPLOY_DIR/" 2>/dev/null || true

echo "📄 Adding generic installation guide…"
cp docs/INSTALL.md "$DEPLOY_DIR/"

echo "✅ System package ready in $DEPLOY_DIR"