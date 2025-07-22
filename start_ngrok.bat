@echo off
ECHO This window provides the public internet connection.
ECHO Please keep this window open. You can minimize it.
cd /d "%~dp0"
ngrok http 5000