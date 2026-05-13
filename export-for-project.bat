@echo off
setlocal enabledelayedexpansion

set "WIKI=%~dp0wiki"
set "DEST=%~dp0export_flat"

if not exist "%WIKI%" (
    echo.
    echo [오류] wiki\ 폴더를 찾을 수 없습니다.
    echo.
    echo 이 파일은 FM-WIKI 레포 폴더 안에서 실행해야 합니다.
    echo   올바른 위치 예: D:\FM wiki\export-for-project.bat
    echo   현재 실행 위치: %~dp0
    echo.
    echo FM-WIKI 폴더로 이동한 뒤 다시 실행하세요.
    pause
    exit /b 1
)

if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%"

pushd "%WIKI%"
for /R . %%F in (*.md) do (
    set "subpath=%%~pF"
    if "!subpath:~0,2!" == ".\" set "subpath=!subpath:~2!"
    if "!subpath:~-1!" == "\" set "subpath=!subpath:~0,-1!"
    set "subpath=!subpath:\=_!"
    if "!subpath!" == "" (
        copy "%%F" "%DEST%\%%~nxF" >nul
    ) else (
        copy "%%F" "%DEST%\!subpath!_%%~nxF" >nul
    )
)
popd

echo.
echo 완료: export_flat\ 폴더의 파일을 claude.ai Projects 에 업로드하세요.
for /f %%n in ('dir /b "%DEST%\*.md" 2^>nul ^| find /c /v ""') do echo 파일 수: %%n 개
pause
