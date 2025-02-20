# Requires administrator privileges
# Run this script as administrator

$TaskName = "MalawiProjectsChatbot"
$WorkingDirectory = $PSScriptRoot
$BatchFile = Join-Path $WorkingDirectory "run_server.bat"

# Remove existing task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Create the task action
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$BatchFile`"" `
    -WorkingDirectory $WorkingDirectory

# Create trigger for startup
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Set task settings
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register the task
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Malawi Projects Chatbot FastAPI Server" `
    -RunLevel Highest `
    -Force

# Start the task
Start-ScheduledTask -TaskName $TaskName

Write-Host "Task installed and started successfully!"
Write-Host "You can manage the task using:"
Write-Host "- Task Scheduler (taskschd.msc)"
Write-Host "- PowerShell commands:"
Write-Host "  Start-ScheduledTask -TaskName $TaskName"
Write-Host "  Stop-ScheduledTask -TaskName $TaskName"
Write-Host "  Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo"
