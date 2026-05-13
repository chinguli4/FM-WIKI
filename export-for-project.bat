@echo off
setlocal enabledelayedexpansion

set "DEST=%~dp0export_flat"

if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%"

pushd "%~dp0wiki"
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
