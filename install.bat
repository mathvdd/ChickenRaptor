@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt

@echo off

powershell ^
 "$ws = New-Object -ComObject WScript.Shell;" ^
 "$desktop = [Environment]::GetFolderPath('Desktop');" ^
 "$s = $ws.CreateShortcut((Join-Path $desktop 'ChickenRaptor.lnk'));" ^
 "$s.TargetPath = 'pythonw.exe';" ^
 "$s.Arguments = '""%~dp0bin\app.py""';" ^
 "$s.WorkingDirectory = '%~dp0';" ^
 "$s.IconLocation = '%~dp0assets\ChickenRaptor_small.ico';" ^
 "$s.Save()"

echo.
echo created shortcut on desktop
echo.

pause