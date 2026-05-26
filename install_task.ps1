$ErrorActionPreference = "Stop"
$taskName = "EestiKeeleBot"
$python = "C:\Users\serge\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$script = "C:\Users\serge\Desktop\eesti-keele-bot\bot.py"

# Remove old task if exists
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute $python -Argument $script
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Limited -Force

Write-Host "Done! Task '$taskName' created successfully."
