#!/usr/bin/env bash
set -euo pipefail

echo "🐳 FinanceCommander AI Portal — Docker Smoke Test"
echo "================================================="

# Create temporary .env if not exists
if [ ! -f .env ]; then
    echo "Creating temporary .env for smoke test..."
    cat > .env << EOF
DB_USER=portal
DB_PASSWORD=smoketest123
JWT_SECRET_KEY=smoke-test-secret-key
ANTHROPIC_API_KEY=test-key
OPENAI_API_KEY=test-key
XAI_API_KEY=test-key
GOOGLE_API_KEY=test-key
EOF
    CLEANUP_ENV=true
else
    CLEANUP_ENV=false
fi

cleanup() {
    echo "Cleaning up..."
    docker compose -f docker-compose.v2.yml down -v 2>/dev/null || true
    if [ "$CLEANUP_ENV" = true ]; then
        rm -f .env
    fi
}
trap cleanup EXIT

echo "Building and starting services..."
docker compose -f docker-compose.v2.yml up -d --build

echo "Waiting for PostgreSQL (max 60s)..."
for i in $(seq 1 30); do
    if docker compose -f docker-compose.v2.yml exec -T db pg_isready -U portal -d ai_portal 2>/dev/null; then
        echo "  ✅ PostgreSQL ready"
        break
    fi
    sleep 2
done

echo "Waiting for backend (max 60s)..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "  ✅ Backend healthy"
        break
    fi
    sleep 2
done

echo "Waiting for frontend (max 30s)..."
for i in $(seq 1 15); do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        echo "  ✅ Frontend serving"
        break
    fi
    sleep 2
done

echo ""
echo "Running health checks..."

# Backend health
HEALTH=$(curl -sf http://localhost:8000/health 2>/dev/null || echo '{"status":"unreachable"}')
echo "  Backend:  $HEALTH"

# Frontend serves HTML
if curl -sf http://localhost:3000 | grep -q "html" 2>/dev/null; then
    echo "  Frontend: ✅ Serving HTML"
else
    echo "  Frontend: ❌ Not serving"
fi

# API proxy
if curl -sf http://localhost:3000/health > /dev/null 2>&1; then
    echo "  API Proxy: ✅ Working"
else
    echo "  API Proxy: ❌ Not proxying"
fi

# Specialists endpoint
SPECIALISTS=$(curl -sf http://localhost:8000/specialists/ 2>/dev/null || echo "unreachable")
echo "  Specialists: $SPECIALISTS" | head -c 200

echo ""
echo "================================================="
echo "🎉 Docker smoke test complete!"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"