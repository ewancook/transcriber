#!/bin/bash
source env/bin/activate
pyinstaller --name="transcriber" --windowed --onefile run.py
mv dist/transposer .
rm -r dist/ build/
rm transcriber.spec
