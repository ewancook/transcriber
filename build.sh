#!/bin/bash
source env/bin/activate
pyinstaller --name="transcriber" --windowed --onedir run.py
rm -r build/
rm transcriber.spec
