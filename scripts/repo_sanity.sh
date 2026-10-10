#!/usr/bin/env bash
set +e
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "$0")/.." && pwd))"
echo "=== Broken symlinks ==="
find "$ROOT" -xtype l 2>/dev/null
echo "=== Empty dirs (excluding __pycache__) ==="
find "$ROOT" -type d -empty ! -path "*__pycache__*" 2>/dev/null
echo "=== Files >100MB ==="
find "$ROOT" -type f -size +100M 2>/dev/null
echo "=== Orphan __pycache__ ==="
find "$ROOT" -type d -name __pycache__ -exec dirname {} \; | sort -u
echo "=== Required files ==="
for req in README.md PROGRESS.md CONTRIBUTING.md pyproject.toml requirements.txt environment.yml .gitignore Makefile; do
    [ -f "$ROOT/$req" ] && echo "  ✓ $req" || echo "  ✗ MISSING: $req"
done
