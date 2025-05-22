Set-Location -Path $PSScriptRoot
Write-Output "Activating the venv..."
.venv\Scripts\Activate.ps1
Write-Output "Running main.py..."
pythonw.exe main.py #pythonw instead of python to prevent showing a terminal
Write-Output "Ending."