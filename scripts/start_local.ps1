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

    $pipPathWindows = Join-Path -Path "$backendPath/.venv" -ChildPath 'Scripts/pip.exe'
    $pipPathUnix = Join-Path -Path "$backendPath/.venv" -ChildPath 'bin/pip'

    if (Test-Path $pipPathWindows) {
        $pipPath = $pipPathWindows
    } elseif (Test-Path $pipPathUnix) {
        $pipPath = $pipPathUnix
    } else {
        throw "pip が見つかりませんでした: $pipPathWindows または $pipPathUnix を確認してください。"
    }

    & $pipPath install --upgrade pip
    & $pipPath install -r "$backendPath/requirements.txt"

    Write-Host '=== Frontend セットアップ ==='
    Push-Location $frontendPath
    npm install
    Pop-Location
}

Write-Host '=== Backend 起動 ==='
Write-Host '=== Python 実行ファイルの確認 ==='
$pythonPathWindows = Join-Path -Path "$backendPath/.venv" -ChildPath 'Scripts/python.exe'
$pythonPathUnix = Join-Path -Path "$backendPath/.venv" -ChildPath 'bin/python'

if (Test-Path $pythonPathWindows) {
    $pythonPath = $pythonPathWindows
} elseif (Test-Path $pythonPathUnix) {
    $pythonPath = $pythonPathUnix
} else {
    throw "Python 実行ファイルが見つかりませんでした: $pythonPathWindows または $pythonPathUnix を確認してください。"
}

Start-Process -FilePath $pythonPath -ArgumentList 'run.py' -WorkingDirectory $backendPath

Start-Sleep -Seconds 3

Write-Host '=== Frontend 起動 ==='
Push-Location $frontendPath
npm run dev -- --host
Pop-Location
