#!/bin/bash
# Quick deploy — rebuilds and restarts the AI Portal backend container
# Usage: bash deploy.sh

set -e
cd "$(dirname "$0")"

echo "==> Stashing local changes..."
git stash --include-untracked 2>/dev/null || true

echo "==> Pulling latest code..."
git pull origin main

echo "==> Rebuilding backend container..."
docker compose -f docker-compose.v2.yml up -d --build backend

echo "==> Waiting for health check..."
sleep 8
curl -sf http://localhost:8000/health && echo " ✓ Backend healthy" || echo " ✗ Backend not ready yet — check: docker logs fc-portal-backend"

echo "==> Done."
