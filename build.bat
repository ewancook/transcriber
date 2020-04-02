@echo off
CALL env\Scripts\activate.bat
pyinstaller --name="transcriber" --windowed --onedir run.py
RMDIR /s /q build
DEL /s /q transcriber.spec