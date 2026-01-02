#!/bin/bash
set -e  # Exit on error
set -u  # Exit on undefined variable

# YAML Migration Refresh Script
# This script regenerates all question data in YAML format

echo "================================================"
echo "Starting YAML Migration Refresh"
echo "================================================"
echo ""

# 1. Backup old extracted questions
echo "[1/7] Backing up old extracted questions..."
if [ -d "data/questions-extracted" ] && [ "$(ls -A data/questions-extracted 2>/dev/null)" ]; then
    # Create backup directory with timestamp
    BACKUP_DIR="backups/questions-extracted-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r data/questions-extracted/* "$BACKUP_DIR/"
    echo "  ✓ Backed up extracted questions to $BACKUP_DIR/"
    rm -rf data/questions-extracted/*
    echo "  ✓ Removed old extracted questions"
else
    echo "  → No extracted questions found to backup"
fi
echo ""

# 2. Regenerate extracted questions (YAML)
echo "[2/7] Regenerating extracted questions in YAML format..."
uv run mw extract refresh-all
echo "  ✓ Extracted questions regenerated"
echo ""

# 3. Backup and delete old formatted files
echo "[3/7] Backing up and deleting old formatted files..."
if ls data/questions-formatted/*/q*.json 1> /dev/null 2>&1; then
    # Create backup directory with timestamp
    BACKUP_DIR="backups/questions-formatted-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r data/questions-formatted "$BACKUP_DIR/"
    echo "  ✓ Backed up formatted questions to $BACKUP_DIR/"
    rm -rf data/questions-formatted/*/q*.json
    echo "  ✓ Removed old formatted JSON files"
else
    echo "  → No old formatted files found"
fi
echo ""

# 4. Regenerate formatted questions (YAML)
echo "[4/7] Regenerating formatted questions in YAML format..."
uv run mw format refresh-all
echo "  ✓ Formatted questions regenerated"
echo ""

# 5. Create new vector store
echo "[5/7] Creating new vector store..."
VECTOR_STORE_OUTPUT=$(uv run mw vs create --name "mathwizard-$(date +%Y%m%d)" --update-id)
echo "$VECTOR_STORE_OUTPUT"
echo ""

# 6. Add all YAML questions to vector store
echo "[6/7] Adding YAML questions to vector store..."
uv run mw vs add-all
echo "  ✓ All questions added to vector store"
echo ""

# 7. Run tests
echo "[7/7] Running tests..."
uv run pytest -xvs
echo ""

echo "================================================"
echo "YAML Migration Refresh Complete!"
echo "================================================"