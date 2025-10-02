Param(
    [switch]$Install
)

$ErrorActionPreference = 'Stop'

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDirectory
$backendPath = Join-Path -Path $projectRoot -ChildPath 'backend'
$frontendPath = Join-Path -Path $projectRoot -ChildPath 'frontend'

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
