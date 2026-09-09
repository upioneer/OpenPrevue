#!/usr/bin/env bash
# OpenPrevue Host In-Place Update Companion
# Monitors persistent data directory for .update_trigger and executes
# docker compose pull and up -d independently without third-party containers.

set -euo pipefail

DATA_DIR="${OPENPREVUE_DATA_DIR:-./data}"
TRIGGER_FILE="${DATA_DIR}/.update_trigger"
COMPOSE_FILE="${OPENPREVUE_COMPOSE_FILE:-docker-compose.yml}"
POLL_INTERVAL="${OPENPREVUE_POLL_INTERVAL:-15}"
MODE="watch"

for arg in "$@"; do
    case "$arg" in
        --once)
            MODE="once"
            ;;
        --watch)
            MODE="watch"
            ;;
        --help|-h)
            echo "Usage: $0 [--once | --watch]"
            echo "  --once   Check for .update_trigger once and exit"
            echo "  --watch  Run continuously, polling every ${POLL_INTERVAL} seconds"
            exit 0
            ;;
    esac
done

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [OpenPrevue Updater] $1"
}

check_and_apply_update() {
    if [[ ! -f "${TRIGGER_FILE}" ]]; then
        return 0
    fi

    log "Update trigger detected at ${TRIGGER_FILE}"
    
    TARGET_VERSION="latest"
    if command -v jq >/dev/null 2>&1; then
        TARGET_VERSION=$(jq -r '.target_version // "latest"' "${TRIGGER_FILE}")
    fi
    log "Initiating container upgrade to target version: ${TARGET_VERSION}"

    if command -v docker >/dev/null 2>&1; then
        log "Pulling latest image: docker compose -f ${COMPOSE_FILE} pull..."
        docker compose -f "${COMPOSE_FILE}" pull || {
            log "Warning: docker compose pull returned non-zero. Attempting docker-compose legacy..."
            docker-compose -f "${COMPOSE_FILE}" pull || true
        }

        log "Recreating containers: docker compose -f ${COMPOSE_FILE} up -d..."
        docker compose -f "${COMPOSE_FILE}" up -d || {
            log "Warning: docker compose up -d failed. Attempting docker-compose legacy..."
            docker-compose -f "${COMPOSE_FILE}" up -d
        }

        log "Container replacement completed successfully."
        rm -f "${TRIGGER_FILE}"
        log "Cleaned up trigger file: ${TRIGGER_FILE}"
    else
        log "Error: docker binary not found on host PATH. Cannot apply update."
        exit 1
    fi
}

log "Starting OpenPrevue host updater companion (Mode: ${MODE})."
log "Watching trigger file: ${TRIGGER_FILE}"

if [[ "${MODE}" == "once" ]]; then
    check_and_apply_update
    exit 0
fi

while true; do
    check_and_apply_update
    sleep "${POLL_INTERVAL}"
done
