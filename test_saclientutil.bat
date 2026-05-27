@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ============================================================
REM HCL AppScan Source / ASoC Automation Script
REM ============================================================

REM =========================
REM CONFIGURATION
REM =========================

REM Path to SAClientUtil bin directory
set APPSCAN_BIN=C:\SAClientUtil\bin

REM AppScan CLI executable
set APPSCAN_CMD=%APPSCAN_BIN%\appscan.bat

REM ASoC API Credentials
set KEY_ID=YOUR_KEY_ID
set KEY_SECRET=YOUR_KEY_SECRET

REM Application Name
set APPLICATION_NAME=My Demo App

REM Source Code Directory
set SOURCE_DIR=C:\code\myapp

REM IRX Output Directory
set IRX_OUTPUT_DIR=C:\irx

REM IRX Filename
set IRX_NAME=myapp.irx

REM Scan Name
set SCAN_NAME=Automated SAST Scan

REM Report Output
set REPORT_FILE=C:\reports\scan_results.html

REM ============================================================
REM VERIFY CLI EXISTS
REM ============================================================

if not exist "%APPSCAN_CMD%" (
    echo.
    echo ERROR: Could not find:
    echo %APPSCAN_CMD%
    pause
    exit /b 1
)

REM ============================================================
REM LOGIN
REM ============================================================

echo.
echo ============================================================
echo LOGIN TO ASOC
echo ============================================================

call "%APPSCAN_CMD%" api_login ^
    -u %KEY_ID% ^
    -P %KEY_SECRET%

if errorlevel 1 (
    echo Login failed.
    pause
    exit /b 1
)

REM ============================================================
REM PREPARE IRX
REM ============================================================

echo.
echo ============================================================
echo PREPARING IRX PACKAGE
echo ============================================================

call "%APPSCAN_CMD%" prepare ^
    -d "%IRX_OUTPUT_DIR%" ^
    -n "%IRX_NAME%" ^
    "%SOURCE_DIR%"

if errorlevel 1 (
    echo IRX preparation failed.
    pause
    exit /b 1
)

REM ============================================================
REM START SCAN
REM ============================================================

echo.
echo ============================================================
echo STARTING SCAN
echo ============================================================

call "%APPSCAN_CMD%" queue_analysis ^
    -a "%APPLICATION_NAME%" ^
    -f "%IRX_OUTPUT_DIR%\%IRX_NAME%" ^
    --scanname "%SCAN_NAME%"

if errorlevel 1 (
    echo Scan submission failed.
    pause
    exit /b 1
)

REM ============================================================
REM OPTIONAL - CHECK SCAN STATUS
REM ============================================================

echo.
echo ============================================================
echo CHECK SCAN STATUS
echo ============================================================

echo.
echo Use the following command to check scan status:
echo.
echo appscan.bat list_scans
echo.

REM ============================================================
REM OPTIONAL - GENERATE REPORT
REM ============================================================

echo.
echo ============================================================
echo GENERATE REPORT
echo ============================================================

echo.
echo Example:
echo.
echo appscan.bat generate_report -i SCAN_ID -o "%REPORT_FILE%"
echo.

echo.
echo ============================================================
echo COMPLETED
echo ============================================================

pause
