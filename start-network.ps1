param(
    [int]$Port = 8000
)

Write-Host "Starting JCL Inventory and Cashier for other computers and phones..."
Write-Host ""
Write-Host "Open one of these IPv4 addresses from another device on the same Wi-Fi/LAN:"
ipconfig | Select-String "IPv4 Address"
Write-Host ""
Write-Host "Use: http://<IPv4-address>:$Port/"
Write-Host ""

$env:DEBUG = "True"
$env:SECURE_SSL_REDIRECT = "False"
$env:SESSION_COOKIE_SECURE = "False"
$env:CSRF_COOKIE_SECURE = "False"
$env:ALLOWED_HOSTS = "*"

python manage.py runserver "0.0.0.0:$Port"
