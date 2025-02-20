# Requires administrator privileges
# Run this script as administrator

$ServiceName = "MalawiProjectsChatbot"
$ServiceDisplayName = "Malawi Projects Chatbot"
$ServiceDescription = "FastAPI service for Malawi Projects Chatbot"
$WorkingDirectory = $PSScriptRoot
$BatchFile = Join-Path $WorkingDirectory "run_server.bat"

# Extract NSSM
Expand-Archive -Path "nssm.zip" -DestinationPath "." -Force
$NSSMPath = Join-Path $WorkingDirectory "nssm-2.24\win64\nssm.exe"

# Remove existing service if it exists
& $NSSMPath stop $ServiceName
& $NSSMPath remove $ServiceName confirm

# Install new service
& $NSSMPath install $ServiceName $BatchFile

# Configure service
& $NSSMPath set $ServiceName DisplayName $ServiceDisplayName
& $NSSMPath set $ServiceName Description $ServiceDescription
& $NSSMPath set $ServiceName AppDirectory $WorkingDirectory
& $NSSMPath set $ServiceName AppExit Default Restart
& $NSSMPath set $ServiceName AppRestartDelay 10000
& $NSSMPath set $ServiceName AppStdout (Join-Path $WorkingDirectory "logs\service.log")
& $NSSMPath set $ServiceName AppStderr (Join-Path $WorkingDirectory "logs\error.log")

# Create logs directory
New-Item -ItemType Directory -Force -Path (Join-Path $WorkingDirectory "logs")

# Start the service
& $NSSMPath start $ServiceName

Write-Host "Service installed and started successfully!"
Write-Host "You can manage the service using:"
Write-Host "- Services.msc"
Write-Host "- sc start/stop $ServiceName"
Write-Host "- nssm start/stop/restart $ServiceName"
Write-Host ""
Write-Host "Logs are available in the logs directory:"
Write-Host "- Service log: logs\service.log"
Write-Host "- Error log: logs\error.log"
