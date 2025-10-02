@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%scripts\start_local.ps1"

where powershell >nul 2>&1
if %ERRORLEVEL%==0 (
    set "POWERSHELL_EXE=powershell"
) else (
    where pwsh >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "POWERSHELL_EXE=pwsh"
    ) else (
        echo PowerShell が見つかりませんでした。Windows PowerShell もしくは PowerShell 7 をインストールしてください。
        exit /b 1
    )
)

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo スクリプトの実行中にエラーが発生しました。上記のメッセージを確認してください。
    pause
)

exit /b %EXIT_CODE%
