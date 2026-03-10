#!/bin/sh
# Copy mounted SSH key to a writable location with correct permissions
if [ -f /mnt/ssh-key/id_ed25519 ]; then
    cp /mnt/ssh-key/id_ed25519 /root/.ssh/id_ed25519
    chmod 600 /root/.ssh/id_ed25519
fi
exec "$@"
