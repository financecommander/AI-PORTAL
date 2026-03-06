#!/usr/bin/env bash
# deploy-blueprint.sh — Deploy Blueprint Editor integration
#
# Run from the AI-PORTAL directory on fc-ai-portal (34.139.78.75):
#   chmod +x deploy-blueprint.sh && ./deploy-blueprint.sh
#
# Architecture:
#   AI-PORTAL frontend (port 3000) → nginx → backend (port 8000)  → /api/v2/blueprint
#                                    nginx → swarm-mainframe (10.142.0.4:8080) → /swarm/api/v1/blueprint
#   Triton models served from swarm-gpu (10.142.0.6:8000)

set -euo pipefail

echo "╔══════════════════════════════════════════════╗"
echo "║  Blueprint Editor Deployment — AI-PORTAL     ║"
echo "╚══════════════════════════════════════════════╝"

# ── 1. Install Orchestra DSL package ─────────────────────────────────
echo ""
echo "→ Installing Orchestra DSL package..."
pip install --quiet orchestra-dsl 2>/dev/null || {
    echo "  orchestra-dsl not on PyPI, installing from git..."
    pip install --quiet "git+https://github.com/financecommander/Orchestra.git" || {
        echo "  ⚠ Could not install orchestra-dsl. Blueprint parse/validate/generate will fail."
        echo "  Install manually: pip install -e /path/to/Orchestra"
    }
}

# ── 2. Rebuild Docker containers ────────────────────────────────────
echo ""
echo "→ Rebuilding containers with Blueprint support..."
docker compose -f docker-compose.v2.yml build --no-cache backend
docker compose -f docker-compose.v2.yml up -d backend

echo ""
echo "→ Waiting for backend health check..."
for i in {1..30}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✓ Backend healthy"
        break
    fi
    sleep 2
    if [ "$i" -eq 30 ]; then
        echo "  ✗ Backend did not become healthy in 60s"
        exit 1
    fi
done

# ── 3. Rebuild frontend ─────────────────────────────────────────────
echo ""
echo "→ Rebuilding frontend with Blueprint Editor component..."
docker compose -f docker-compose.v2.yml build --no-cache frontend
docker compose -f docker-compose.v2.yml up -d frontend

echo ""
echo "→ Waiting for frontend..."
for i in {1..20}; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo "  ✓ Frontend serving"
        break
    fi
    sleep 2
done

# ── 4. Verify endpoints ─────────────────────────────────────────────
echo ""
echo "→ Verifying Blueprint endpoints..."

STATUS_BACKEND=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:8000/api/v2/blueprint/sessions || echo "000")
if [ "$STATUS_BACKEND" = "200" ]; then
    echo "  ✓ Backend /api/v2/blueprint/sessions → 200 OK"
else
    echo "  ⚠ Backend /api/v2/blueprint/sessions → $STATUS_BACKEND"
fi

STATUS_SWARM=$(curl -sf -o /dev/null -w "%{http_code}" http://10.142.0.4:8080/api/v1/blueprint/test/execute 2>/dev/null || echo "000")
echo "  ℹ Swarm Blueprint endpoint → $STATUS_SWARM (404 expected for test path)"

echo ""
echo "═══════════════════════════════════════════════"
echo "Blueprint Editor deployed successfully!"
echo ""
echo "Access: Login to AI Portal → Swarm Mainframe → Blueprint button"
echo "═══════════════════════════════════════════════"
