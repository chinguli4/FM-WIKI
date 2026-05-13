@echo off
setlocal enabledelayedexpansion

rem --- 레포 위치 탐색 ---
set "REPO=%~dp0"
if exist "%REPO%wiki\" goto :found

echo.
echo FM-WIKI 레포 폴더 경로를 입력하세요.
echo 예: C:\Users\홍길동\FM-WIKI
echo.
set /p "REPO=경로: "
if "!REPO!" == "" goto :error
if "!REPO:~-1!" NEQ "\" set "REPO=!REPO!\"
if not exist "!REPO!wiki\" goto :error
goto :found

:error
echo.
echo [오류] 해당 경로에 wiki\ 폴더가 없습니다.
echo FM-WIKI 레포를 올바르게 복제했는지 확인하세요.
pause
exit /b 1

:found
set "WIKI=%REPO%wiki"
set "DEST=%REPO%export_flat"

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
echo 완료: %DEST%
echo 위 폴더의 파일을 claude.ai Projects 에 업로드하세요.
for /f %%n in ('dir /b "%DEST%\*.md" 2^>nul ^| find /c /v ""') do echo 파일 수: %%n 개
pause
