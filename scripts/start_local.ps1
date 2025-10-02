Param(
    [switch]$Install
)

[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

$ErrorActionPreference = 'Stop'

function Get-VenvPythonPath {
    param(
        [string]$VenvPath
    )

    $candidates = @(
        Join-Path -Path $VenvPath -ChildPath 'Scripts/python.exe',
        Join-Path -Path $VenvPath -ChildPath 'bin/python'
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Get-VenvPipPath {
    param(
        [string]$VenvPath
    )

    $candidates = @(
        Join-Path -Path $VenvPath -ChildPath 'Scripts/pip.exe',
        Join-Path -Path $VenvPath -ChildPath 'bin/pip'
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Get-CommandPath {
    param(
        [System.Management.Automation.CommandInfo]$Command
    )

    if (-not $Command) {
        return $null
    }

    if ($Command.Source) {
        return $Command.Source
    }

    if ($Command.PSObject.Properties['Path']) {
        return $Command.Path
    }

    return $Command.Definition
}

function New-VirtualEnvironment {
    param(
        [string]$VenvPath
    )

    $pythonBootstrapCandidates = @('python', 'python3')

    foreach ($candidate in $pythonBootstrapCandidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        $commandPath = Get-CommandPath -Command $command
        if ($commandPath) {
            Write-Host "=== $($command.Name) を使用して仮想環境を作成します ==="
            & $commandPath -m venv $VenvPath
            return
        }
    }

    $pyLauncher = Get-Command 'py' -ErrorAction SilentlyContinue
    $pyLauncherPath = Get-CommandPath -Command $pyLauncher
    if ($pyLauncherPath) {
        Write-Host '=== py ランチャーを使用して仮想環境を作成します ==='
        & $pyLauncherPath -3 -m venv $VenvPath
        return
    }

    throw "Python が見つかりませんでした。Python 3.x をインストールし、パスを通してください。"
}

function Ensure-BackendVirtualEnvironment {
    param(
        [string]$VenvPath
    )

    $pythonPath = Get-VenvPythonPath -VenvPath $VenvPath
    $isNew = $false

    if (-not $pythonPath) {
        Write-Host '=== 仮想環境が存在しないため新規作成します ==='
        New-VirtualEnvironment -VenvPath $VenvPath
        $pythonPath = Get-VenvPythonPath -VenvPath $VenvPath
        $isNew = $true
    }

    if (-not $pythonPath) {
        throw "仮想環境の Python 実行ファイルを取得できませんでした: $VenvPath"
    }

    return [PSCustomObject]@{
        PythonPath = $pythonPath
        IsNew      = $isNew
    }
}

function Install-BackendDependencies {
    param(
        [string]$VenvPath,
        [string]$BackendPath
    )

    $pipPath = Get-VenvPipPath -VenvPath $VenvPath

    if (-not $pipPath) {
        throw "pip が見つかりませんでした: $VenvPath の仮想環境を確認してください。"
    }

    Write-Host '=== Backend 依存関係のインストール ==='
    & $pipPath install --upgrade pip
    $requirementsPath = Join-Path -Path $BackendPath -ChildPath 'requirements.txt'
    & $pipPath install -r $requirementsPath
}

function Ensure-FrontendDependencies {
    param(
        [string]$FrontendPath,
        [switch]$ForceInstall
    )

    $nodeModulesPath = Join-Path -Path $FrontendPath -ChildPath 'node_modules'

    if ($ForceInstall -or -not (Test-Path $nodeModulesPath)) {
        $npmCommand = Get-Command 'npm' -ErrorAction SilentlyContinue
        if (-not $npmCommand) {
            throw 'npm コマンドが見つかりませんでした。Node.js をインストールし、パスを通してください。'
        }

        Write-Host '=== Frontend セットアップ ==='
        Push-Location $FrontendPath
        npm install
        Pop-Location
    }
}

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDirectory
$backendPath = Join-Path -Path $projectRoot -ChildPath 'backend'
$frontendPath = Join-Path -Path $projectRoot -ChildPath 'frontend'
$backendVenvPath = Join-Path -Path $backendPath -ChildPath '.venv'

Write-Host '=== Backend 仮想環境の確認 ==='
$venvInfo = Ensure-BackendVirtualEnvironment -VenvPath $backendVenvPath
$pythonPath = $venvInfo.PythonPath

$shouldInstallBackendDeps = $Install -or $venvInfo.IsNew
if ($shouldInstallBackendDeps) {
    Install-BackendDependencies -VenvPath $backendVenvPath -BackendPath $backendPath
}

Ensure-FrontendDependencies -FrontendPath $frontendPath -ForceInstall:$Install

Write-Host '=== Backend 起動 ==='
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList 'run.py' -WorkingDirectory $backendPath -PassThru

$didPushLocation = $false

try {
    Start-Sleep -Seconds 3

    Write-Host '=== Frontend 起動 ==='
    Write-Host 'ブラウザで http://localhost:8080 にアクセスできます。' -ForegroundColor Cyan
    Push-Location $frontendPath
    $didPushLocation = $true
    npm run dev -- --host
}
finally {
    if ($didPushLocation) {
        Pop-Location
    }

    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host '=== Backend 停止 ==='
        try {
            Stop-Process -Id $backendProcess.Id -ErrorAction Stop
        }
        catch {
            Write-Warning "バックエンド プロセスの停止に失敗しました: $($_.Exception.Message)"
        }
    }
}

Write-Host 'ローカル開発環境を終了しました。'
