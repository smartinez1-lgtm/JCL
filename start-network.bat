@echo off
set PORT=8000
if not "%~1"=="" set PORT=%~1

echo Starting JCL Inventory and Cashier for other computers and phones...
echo.
echo Open one of these IPv4 addresses from another device on the same Wi-Fi/LAN:
ipconfig | findstr /C:"IPv4 Address"
echo.
echo Use: http://^<IPv4-address^>:%PORT%/
echo.

set DEBUG=True
set SECURE_SSL_REDIRECT=False
set SESSION_COOKIE_SECURE=False
set CSRF_COOKIE_SECURE=False
set ALLOWED_HOSTS=*

python manage.py runserver 0.0.0.0:%PORT%
