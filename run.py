#!/usr/bin/env python3
import sys

from PyQt5 import QtWidgets

from transcriber.transcriber.transcriber import Transcriber

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    transcriber = Transcriber()
    transcriber.show()
    sys.exit(app.exec_())
