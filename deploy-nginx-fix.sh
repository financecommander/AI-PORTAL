#!/bin/bash
set -e
cd /workspaces/AI-PORTAL 2>/dev/null || cd ~/AI-PORTAL 2>/dev/null || { echo "❌"; exit 1; }
mkdir -p 'frontend'
cat > 'frontend/nginx.conf' << 'FILEEOF_nginx'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — all routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /auth {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /chat {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        chunked_transfer_encoding on;
    }

    location /specialists {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
    }

    # WebSocket endpoint for pipeline streaming
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    location /usage {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /conversations {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://backend:8000;
    }
}

FILEEOF_nginx
echo "✅ nginx.conf updated"
git add -A
git commit --no-gpg-sign -m "fix: nginx SSE streaming + conversations proxy

/chat: added proxy_buffering off, proxy_cache off, 300s timeouts for SSE streaming
/conversations: new proxy route for conversation history API
Without proxy_buffering off, nginx buffers SSE chunks and chat appears empty." || echo "Nothing"
git push origin main
echo "✅ Pushed. Frontend rebuild:"
echo "  cd ~/AI-PORTAL && git fetch origin main && git reset --hard origin/main"
echo "  sudo docker compose -f docker-compose.v2.yml build --no-cache frontend"
echo "  sudo docker compose -f docker-compose.v2.yml up -d --force-recreate"
