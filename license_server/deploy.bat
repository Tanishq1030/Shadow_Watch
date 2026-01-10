@echo off
REM Deploy Shadow Watch License Server to Fly.io
REM Usage: deploy.bat

echo 🚀 Deploying Shadow Watch License Server to Fly.io...

REM Check if Fly CLI is installed
where flyctl >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing Fly CLI...
    powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    echo ✅ Fly CLI installed
    echo ℹ️  Please close and reopen CMD, then run this script again
    pause
    exit /b
)

REM Login to Fly.io
echo 🔐 Logging in to Fly.io...
flyctl auth login

REM Initialize Fly.io app (if not already done)
if not exist fly.toml (
    echo 📝 Initializing Fly.io app...
    flyctl launch --name shadowwatch-license --region ord --no-deploy --org personal
)

REM Create persistent volume for SQLite
echo 💾 Creating persistent volume...
flyctl volumes list | findstr "license_data" >nul
if %errorlevel% neq 0 (
    flyctl volumes create license_data --size 1 --region ord
    echo ✅ Volume created
) else (
    echo ℹ️  Volume already exists
)

REM Deploy to Fly.io
echo 🚢 Deploying application...
flyctl deploy

REM Show deployment info
echo.
echo ✅ Deployment complete!
echo.
echo 📍 Your license server URL:
flyctl info | findstr "Hostname"

echo.
echo 🔑 Next steps:
echo    1. Generate trial keys:
echo       flyctl ssh console -C "python generate_trial_keys.py"
echo.
echo    2. Test health check:
echo       curl https://shadowwatch-license.fly.dev/
echo.
echo    3. Update Shadow Watch library:
echo       Update shadowwatch/utils/license.py with your Fly.io URL

pause
