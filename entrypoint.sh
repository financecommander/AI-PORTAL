#!/bin/sh
# Copy mounted SSH key to a writable location with correct permissions
# Handles both file and directory mount scenarios
SSH_DIR="/root/.ssh"
STAGING="/mnt/ssh-key/id_ed25519"

mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

if [ -f "$STAGING" ]; then
    cp "$STAGING" "$SSH_DIR/id_ed25519"
    chmod 600 "$SSH_DIR/id_ed25519"
    echo "[entrypoint] SSH key copied from staging (chmod 600)"
elif [ -d "$STAGING" ]; then
    echo "[entrypoint] WARNING: $STAGING is a directory, not a file"
    echo "[entrypoint] The host SSH key may have been corrupted by a previous Docker mount"
    echo "[entrypoint] Regenerate with: ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''"
fi

# Also fix permissions on any existing key (in case it was baked into the image)
if [ -f "$SSH_DIR/id_ed25519" ]; then
    chmod 600 "$SSH_DIR/id_ed25519"
fi

exec "$@"
