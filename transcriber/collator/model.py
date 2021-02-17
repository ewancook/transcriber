import logging
from multiprocessing import Process

from PyQt5 import QtCore

from transcriber.collator import utils


class CollatorModel(QtCore.QObject):
    collation_started = QtCore.pyqtSignal()
    collation_finished = QtCore.pyqtSignal(bool)

    start = QtCore.pyqtSignal(str, list)
    terminate_collation = QtCore.pyqtSignal()

    def __init__(self):
        super(CollatorModel, self).__init__()
        self.connect_start(self.collate)
        self.connect_terminate_collation(self.terminate)
        self.process = None
        self.state = False

    @QtCore.pyqtSlot(str, list)
    def collate(self, collated_file, filenames):
        self.collation_started.emit()
        self.process = Process(
            target=utils.collate,
            args=(
                collated_file,
                filenames,
            ),
        )
        self.process.start()
        self.state = True
        self.process.join()
        if self.state:
            logging.info(
                f"Collation of {len(filenames)} file(s) was successful"
            )
        else:
            logging.error("Collation was cancelled")
        self.collation_finished.emit(self.state)

    @QtCore.pyqtSlot()
    def terminate(self):
        if self.process is not None:
            self.process.terminate()
            self.state = False

    def connect_collation_started(self, slot):
        self.collation_started.connect(slot)

    def connect_collation_finished(self, slot):
        self.collation_finished.connect(slot)

    def connect_start(self, slot):
        self.start.connect(slot)

    def connect_terminate_collation(self, slot):
        self.terminate_collation.connect(slot, QtCore.Qt.DirectConnection)
