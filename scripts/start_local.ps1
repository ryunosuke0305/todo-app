Param(
    [switch]$Install
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot '..' 'backend'
$frontendPath = Join-Path $projectRoot '..' 'frontend'

if ($Install) {
    Write-Host '=== Backend セットアップ ==='
    python -m venv "$backendPath/.venv"
    & "$backendPath/.venv/Scripts/pip.exe" install --upgrade pip
    & "$backendPath/.venv/Scripts/pip.exe" install -r "$backendPath/requirements.txt"

    Write-Host '=== Frontend セットアップ ==='
    Push-Location $frontendPath
    npm install
    Pop-Location
}

Write-Host '=== Backend 起動 ==='
Start-Process -FilePath "$backendPath/.venv/Scripts/python.exe" -ArgumentList 'run.py' -WorkingDirectory $backendPath

Start-Sleep -Seconds 3

Write-Host '=== Frontend 起動 ==='
Push-Location $frontendPath
npm run dev -- --host
Pop-Location
