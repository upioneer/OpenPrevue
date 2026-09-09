#!/bin/sh
set -e

# Turnkey privilege dropping and volume permission reconciliation
PUID=${PUID:-1000}
PGID=${PGID:-1000}

if [ "$(id -u)" = '0' ]; then
    # Ensure appuser and appgroup exist with matching PUID / PGID
    if ! getent group "$PGID" >/dev/null 2>&1; then
        groupmod -o -g "$PGID" appuser >/dev/null 2>&1 || true
    fi
    if [ "$PUID" != "$(id -u appuser 2>/dev/null)" ]; then
        usermod -o -u "$PUID" appuser >/dev/null 2>&1 || true
    fi

    # Ensure persistent data directory exists
    DATA_DIRECTORY="${DATA_DIR:-/app/data}"
    mkdir -p "$DATA_DIRECTORY"

    # Automatically reconcile permissions on mounted volume
    chown -R "$PUID:$PGID" "$DATA_DIRECTORY"
    chmod 775 "$DATA_DIRECTORY"

    # If the Docker socket is mounted, ensure appuser has access
    DOCKER_SOCKET="${DOCKER_SOCKET_PATH:-/var/run/docker.sock}"
    if [ -S "$DOCKER_SOCKET" ]; then
        DOCKER_GID=$(stat -c '%g' "$DOCKER_SOCKET" 2>/dev/null || true)
        if [ -n "$DOCKER_GID" ] && [ "$DOCKER_GID" != "0" ]; then
            if ! getent group "$DOCKER_GID" >/dev/null 2>&1; then
                groupadd -for -g "$DOCKER_GID" docker-host >/dev/null 2>&1 || true
            fi
            usermod -aG "$DOCKER_GID" appuser >/dev/null 2>&1 || true
        fi
    fi

    # Execute command as appuser via gosu
    exec gosu "$PUID:$PGID" "$@"
fi

# Fallback if already running as non-root
exec "$@"
