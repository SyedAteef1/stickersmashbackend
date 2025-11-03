@echo off
echo Adding Windows Firewall rule for ML Server (Port 8001)...
echo.
netsh advfirewall firewall add rule name="ML Server Port 8001" dir=in action=allow protocol=TCP localport=8001
echo.
if %errorlevel% equ 0 (
    echo SUCCESS: Firewall rule added!
    echo Port 8001 is now accessible from network.
) else (
    echo FAILED: Please run this file as Administrator
    echo Right-click and select "Run as administrator"
)
echo.
pause
