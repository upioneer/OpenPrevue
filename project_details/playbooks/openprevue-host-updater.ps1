# OpenPrevue Host In-Place Update Companion (PowerShell)
# Monitors persistent data directory for .update_trigger and executes
# docker compose pull and up -d independently without third-party containers.

param (
    [switch]$Once,
    [int]$IntervalSeconds = 15,
    [string]$DataDir = ".\data",
    [string]$ComposeFile = "docker-compose.yml"
)

$triggerPath = Join-Path $DataDir ".update_trigger"

function Write-UpdaterLog {
    param ([string]$Message)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Host "[$timestamp] [OpenPrevue Updater] $Message"
}

function Invoke-UpdateRoutine {
    if (-not (Test-Path $triggerPath)) {
        return
    }

    Write-UpdaterLog "Update trigger detected at $triggerPath"

    $targetVersion = "latest"
    try {
        $json = Get-Content $triggerPath -Raw | ConvertFrom-Json
        if ($json.target_version) {
            $targetVersion = $json.target_version
        }
    } catch {
        Write-UpdaterLog "Warning: Could not parse trigger JSON. Defaulting target to latest."
    }

    Write-UpdaterLog "Initiating container upgrade to target version: $targetVersion"

    if ((Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-UpdaterLog "Pulling latest images: docker compose -f $ComposeFile pull..."
        docker compose -f $ComposeFile pull
        
        Write-UpdaterLog "Recreating containers: docker compose -f $ComposeFile up -d..."
        docker compose -f $ComposeFile up -d

        Write-UpdaterLog "Container replacement completed successfully."
        Remove-Item -Path $triggerPath -Force -ErrorAction SilentlyContinue
        Write-UpdaterLog "Cleaned up trigger file: $triggerPath"
    } else {
        Write-UpdaterLog "Error: docker binary was not found in host PATH. Cannot apply update."
    }
}

Write-UpdaterLog "Starting OpenPrevue host updater companion (Once: $Once, Interval: ${IntervalSeconds}s)."
Write-UpdaterLog "Watching trigger file: $triggerPath"

if ($Once) {
    Invoke-UpdateRoutine
    exit 0
}

while ($true) {
    Invoke-UpdateRoutine
    Start-Sleep -Seconds $IntervalSeconds
}
