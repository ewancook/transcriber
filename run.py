#!/usr/bin/env python3
from multiprocessing import freeze_support
import sys

from PyQt5 import QtWidgets

from transcriber.transcriber import Transcriber

if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication([])
    transcriber = Transcriber()
    transcriber.show()
    sys.exit(app.exec_())
