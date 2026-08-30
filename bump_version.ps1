param (
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$Version = $Version.TrimStart('v')
Write-Host "Bumping version to $Version..."

# Update frontend package.json
$packageJsonPath = Join-Path $PSScriptRoot "frontend\package.json"
if (Test-Path $packageJsonPath) {
    $content = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $content.version = $Version
    $content | ConvertTo-Json -Depth 10 | Set-Content $packageJsonPath
    Write-Host "Updated frontend/package.json version to $Version"
}

# Update backend main.py
$mainPyPath = Join-Path $PSScriptRoot "backend\app\main.py"
if (Test-Path $mainPyPath) {
    $mainContent = Get-Content $mainPyPath -Raw
    $mainContent = $mainContent -replace 'version="[^"]+"', "version=`"$Version`""
    Set-Content -Path $mainPyPath -Value $mainContent
    Write-Host "Updated backend/app/main.py version to $Version"
}

Write-Host "Version bump to $Version complete."
