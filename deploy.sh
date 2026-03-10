#!/bin/bash
# Quick deploy — rebuilds and restarts the AI Portal backend container
# Usage: bash deploy.sh

set -e
cd "$(dirname "$0")"

echo "==> Pulling latest code..."
git pull origin main

echo "==> Rebuilding backend container..."
docker compose -f docker-compose.v2.yml up -d --build backend

echo "==> Waiting for health check..."
sleep 5
curl -sf http://localhost:8000/health && echo " ✓ Backend healthy" || echo " ✗ Backend not ready yet"

echo "==> Done."
