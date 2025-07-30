#!/usr/bin/env bash
# PicoWDesk – Games Installation
# System + games only; all games prefixed _Games_.

set -e
DEPLOY_DIR="deploy"
SYS_SRC="apps/system"
GAMES_SRC="apps/games"

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

echo "📂 Copying system apps (no virtual folder prefix)…"
for f in "$SYS_SRC"/*.html; do
    [ -e "$f" ] || continue
    cp "$f" "$DEPLOY_DIR/$(basename "$f")"
done
cp "$SYS_SRC"/*.ico "$DEPLOY_DIR/" 2>/dev/null || true

echo "📂 Renaming games for _Games_ virtual folder…"
for g in "$GAMES_SRC"/*.html; do
    [ -e "$g" ] || continue
    cp "$g" "$DEPLOY_DIR/_Games_$(basename "$g")"
done
cp "$GAMES_SRC"/*.ico "$DEPLOY_DIR/" 2>/dev/null || true

echo "📄 Adding generic installation guide…"
cp docs/INSTALL.md "$DEPLOY_DIR/"

echo "✅ Games package ready in $DEPLOY_DIR"