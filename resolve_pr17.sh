#!/bin/bash
set -e

echo "=== Resolving PR #17 Merge Conflicts ==="

# Checkout PR branch
echo "Checking out PR branch..."
git checkout copilot/implement-crewai-pipeline-wrapper

# Merge develop
echo "Merging develop into PR branch..."
git merge origin/develop || {
    echo "Merge conflicts detected, resolving..."
    
    # Resolve conflicts by keeping "ours" (PR branch version)
    git checkout --ours backend/.env.example 2>/dev/null || echo "No conflict in .env.example"
    git checkout --ours backend/main.py 2>/dev/null || echo "No conflict in main.py"
    git checkout --ours backend/routes/__init__.py 2>/dev/null || echo "No conflict in routes/__init__.py"
    
    # Stage resolved files
    git add backend/.env.example backend/main.py backend/routes/__init__.py 2>/dev/null || true
    
    # Complete merge
    git commit -m "fix: resolve merge conflicts — keep PR #17 versions"
}

# Push changes
echo "Pushing changes..."
git push origin copilot/implement-crewai-pipeline-wrapper

echo "=== Done! ==="
git log -1 --oneline
