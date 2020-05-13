#!/usr/bin/env python3
import logging
import sys
from multiprocessing import freeze_support

from PyQt5 import QtWidgets

from transcriber.logger import Logger
from transcriber.transcriber import Transcriber

LOG_FORMAT = "(%(asctime)s) %(message)s"
VERSION = "{TRAVIS_TAG}"


class TranscriberGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(TranscriberGUI, self).__init__()
        self.tabs = QtWidgets.QTabWidget()

        self.transcriber = Transcriber(self)
        self.tabs.addTab(self.transcriber, "Transcriber")

        self.logger = Logger(self)
        self.logger.setFormatter(logging.Formatter(LOG_FORMAT, "%H:%M:%S"))
        logging.getLogger().addHandler(self.logger)
        logging.getLogger().setLevel(logging.DEBUG)
        self.tabs.addTab(self.logger, "Log")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.tabs)

        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self.layout)
        self.setWindowTitle(f"Transcriber {VERSION}")


if __name__ == "__main__":
    freeze_support()
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    transcriber = TranscriberGUI()
    transcriber.show()
    sys.exit(app.exec_())
