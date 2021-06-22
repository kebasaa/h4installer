@echo off
set /p id="Enter Libray to install: "
rem echo .
py %~dp0/install_h4plugins.py %id%
pause