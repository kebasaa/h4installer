@echo off
set /p id="Enter Libray to install: "
echo .
echo %id%
C:/Users/phil/AppData/Local/Arduino15/packages/esp8266/tools/python3/3.7.2-post1/python %~dp0/install_h4plugins.py %id%
pause