@echo off
TITLE Project TIM - Unified Master Setup
COLOR 0A

echo ===================================================
echo     Project TIM - Unified Environment Setup        
echo ===================================================
echo.

:: -----------------------------------------------------
:: STEP 1: Check and Install Git
:: -----------------------------------------------------
echo [1/4] Checking Git installation...
where git >nul 2>&1
if %errorlevel% == 0 (
    echo [+] Git is already installed.
) else (
    echo [*] Git not found. Installing Git automatically...
    where winget >nul 2>&1
    if %errorlevel% == 0 (
        echo [*] Installing via Winget...
        winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
    ) else (
        echo [*] Winget not found. Downloading via PowerShell fallback...
        set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe"
        set "INSTALLER_PATH=%TEMP%\GitInstaller.exe"
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%INSTALLER_PATH%'"
        if exist "%INSTALLER_PATH%" (
            "%INSTALLER_PATH%" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS
            del "%INSTALLER_PATH%" >nul 2>&1
        )
    )
    echo [!] NOTE: You may need to restart your terminal later if git commands fail.
)

echo.
echo ===================================================
echo.

:: -----------------------------------------------------
:: STEP 2: Create Virtual Environment
:: -----------------------------------------------------
echo [2/4] Checking Python Virtual Environment (venv)...
if not exist "venv" (
    echo [*] Creating virtual environment 'venv'...
    py -3.11 -m venv venv 2>nul || python -m venv venv
    if errorlevel 1 (
        echo [!] Failed to create venv. Ensure Python is installed and added to PATH.
        pause
        exit /b
    )
    echo [+] Virtual environment created successfully.
) else (
    echo [+] Virtual environment 'venv' already exists.
)

echo.
echo ===================================================
echo.

:: -----------------------------------------------------
:: STEP 3: Activate Virtual Environment
:: -----------------------------------------------------
echo [3/4] Activating Virtual Environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [!] Activation script not found!
    pause
    exit /b
)
echo [+] Virtual environment activated.

echo.
echo ===================================================
echo.

:: -----------------------------------------------------
:: STEP 4: Install Core Requirements
:: -----------------------------------------------------
echo [4/4] Installing Required Dependencies...
echo [*] Cleaning up potential opencv-python-headless conflicts...
pip uninstall opencv-python-headless -y >nul 2>&1

echo [*] Installing packages...
pip install opencv-python mediapipe==0.10.14 pyautogui numpy

echo.
echo ===================================================
echo [+] All setup tasks completed successfully!
echo ===================================================
echo.

:menu
cls
echo ===================================================
echo            PROJECT TIM - CONTROL MENU
echo ===================================================
echo.
echo  1 ---^> Run Project TIM (Activates venv ^& runs tim.py)
echo  2 ---^> Deactivate / Exit Program
echo.
echo ===================================================
set /p choice="Enter your option (1 or 2): "

if "%choice%"=="1" goto run_tim
if "%choice%"=="2" goto exit_app

:: Handle invalid input
echo.
echo [!] Invalid input! Please enter only 1 or 2.
echo.
timeout /t 2 >nul
goto menu

:run_tim
echo.
echo [*] Checking Virtual Environment...
if exist "venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment 'venv' not found!
    echo [*] Please run main.bat first to set up the environment.
    echo.
    pause
    goto menu
)

echo [*] Starting Project TIM...
echo.
python tim.py

echo.
echo [*] Project TIM has ended. Returning to menu...
echo.
pause
goto menu

:exit_app
echo.
echo [*] Deactivating virtual environment...
call deactivate 2>nul
echo [+] Exiting program...
timeout /t 2 >nul
exit /b
