#!/bin/bash
source env/bin/activate
rm -r dist
pyinstaller --name="transcriber" --windowed --onedir run.py
rm -r build/
rm transcriber.spec
