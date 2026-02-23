@echo off
powershell -ExecutionPolicy Bypass -Command "Get-PnpDevice -Class HIDClass | ForEach-Object { $instance = $_.InstanceId; if ($instance -match 'VID_([0-9A-F]{4})&PID_([0-9A-F]{4})') { $vid = '0x' + $matches[1]; $pidValue = '0x' + $matches[2]; Write-Host 'VID:' $vid ', PID:' $pidValue; Write-Host 'Producto:' $_.FriendlyName; Write-Host ('-' * 40) } }"
pause