#!/bin/bash
source env/bin/activate
pyinstaller --name="transcriber" --windowed --onefile run.py
rm -r build/
rm transcriber.spec
