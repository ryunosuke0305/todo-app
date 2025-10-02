@echo off
setlocal ENABLEEXTENSIONS

chcp 65001 >nul

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "VENV_DIR=%BACKEND_DIR%\.venv"
set "FORCE_INSTALL="

for %%I in (%*) do (
    if /I "%%~I"=="-install" set "FORCE_INSTALL=1"
)

echo === 開発環境セットアップを開始します ===

echo.
echo Python を確認しています...
set "PYTHON_CMD="
set "PYTHON_ARGS="
where python >nul 2>&1
if errorlevel 1 (
    where py >nul 2>&1
    if errorlevel 1 (
        echo Python が見つかりませんでした。Python 3.x をインストールし、パスを通してください。
        goto ERROR
    ) else (
        set "PYTHON_CMD=py"
        set "PYTHON_ARGS=-3"
    )
) else (
    for /f "delims=" %%P in ('where python') do (
        set "PYTHON_CMD=%%P"
        goto AFTER_FIND_PYTHON
    )
)
:AFTER_FIND_PYTHON
if not defined PYTHON_CMD (
    echo Python が見つかりませんでした。Python 3.x をインストールし、パスを通してください。
    goto ERROR
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo 仮想環境を作成しています...
    pushd "%BACKEND_DIR%"
    if defined PYTHON_ARGS (
        "%PYTHON_CMD%" %PYTHON_ARGS% -m venv .venv || (
            popd
            goto ERROR
        )
    ) else (
        "%PYTHON_CMD%" -m venv .venv || (
            popd
            goto ERROR
        )
    )
    popd
    set "FORCE_INSTALL=1"
)

echo.
echo Python 依存関係を確認しています...
if defined FORCE_INSTALL (
    pushd "%BACKEND_DIR%"
    if not exist ".venv\Scripts\activate.bat" (
        echo 仮想環境のアクティベーションスクリプトが見つかりませんでした。
        popd
        goto ERROR
    )
    call ".venv\Scripts\activate.bat"
    if errorlevel 1 (
        echo 仮想環境の有効化に失敗しました。
        popd
        goto ERROR
    )
    python -m pip install --upgrade pip || (
        call deactivate >nul 2>&1
        popd
        goto ERROR
    )
    python -m pip install -r requirements.txt || (
        call deactivate >nul 2>&1
        popd
        goto ERROR
    )
    call deactivate >nul 2>&1
    popd
)

set "NPM_AVAILABLE="
where npm >nul 2>&1
if errorlevel 1 (
    set "NPM_AVAILABLE="
) else (
    set "NPM_AVAILABLE=1"
)

echo.
echo フロントエンド依存関係を確認しています...
set "NEED_NODE_INSTALL="
set "NEED_FRONTEND_BUILD="
if exist "%FRONTEND_DIR%\package.json" (
    if defined FORCE_INSTALL (
        set "NEED_NODE_INSTALL=1"
        set "NEED_FRONTEND_BUILD=1"
    ) else if not exist "%FRONTEND_DIR%\node_modules" (
        set "NEED_NODE_INSTALL=1"
        set "NEED_FRONTEND_BUILD=1"
    ) else if not exist "%FRONTEND_DIR%\dist\index.html" (
        set "NEED_FRONTEND_BUILD=1"
    )
)

if defined NEED_NODE_INSTALL (
    if not defined NPM_AVAILABLE (
        echo npm コマンドが見つかりませんでした。Node.js をインストールし、パスを通してください。
        goto ERROR
    )
    pushd "%FRONTEND_DIR%"
    call npm install
    if errorlevel 1 (
        popd
        goto ERROR
    )
    popd
)

if defined NEED_FRONTEND_BUILD (
    if not defined NPM_AVAILABLE (
        echo npm コマンドが見つからなかったため、フロントエンドをビルドできません。
        goto ERROR
    )
    pushd "%FRONTEND_DIR%"
    call npm run build
    if errorlevel 1 (
        popd
        goto ERROR
    )
    popd
)

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo 仮想環境のアクティベーションスクリプトが見つかりませんでした。
    goto ERROR
)

echo.
echo === サーバーを起動します ===
pushd "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    popd
    goto ERROR
)
set "FRONTEND_DIST_DIR=%FRONTEND_DIR%\dist"
python run.py
set "SERVER_EXIT_CODE=%ERRORLEVEL%"
call deactivate >nul 2>&1
popd
if not "%SERVER_EXIT_CODE%"=="0" (
    echo.
    echo サーバーが異常終了しました。(終了コード %SERVER_EXIT_CODE%)
    goto ERROR
)

echo.
echo サーバーを終了しました。
goto END

:ERROR
echo.
echo 処理中にエラーが発生しました。上記のメッセージを確認してください。
pause
exit /b 1

:END
pause
exit /b 0
