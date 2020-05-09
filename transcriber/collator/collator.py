from itertools import islice
from multiprocessing import Process

from PyQt5 import QtCore

from transcriber.converter.workers import utils


def _collate(save_file, filenames):
    collate_files(
        save_file, [utils.transcribed_filename(f) for f in filenames],
    )


def collate_files(collated_file, filenames):
    with open(filenames[0], "r") as file_with_headers:
        append_file_to_collated(collated_file, file_with_headers)
    for filename in filenames[1:]:
        with open(filename, "r") as file_to_append:
            file_data = islice(file_to_append, 2, None)
            append_file_to_collated(collated_file, file_data)


def append_file_to_collated(collated_file, file_to_append):
    for line in file_to_append:
        collated_file.write(line)
    collated_file.write("\n")


class Collator(QtCore.QObject):
    collation_started = QtCore.pyqtSignal()
    collation_finished = QtCore.pyqtSignal(bool)

    start = QtCore.pyqtSignal(str, list)
    terminate_collation = QtCore.pyqtSignal()

    def __init__(self):
        super(Collator, self).__init__()
        self.start.connect(self.collate)
        self.terminate_collation.connect(
            self.terminate, QtCore.Qt.DirectConnection
        )
        self.process = None
        self.state = False

    @QtCore.pyqtSlot(str, list)
    def collate(self, save_file, filenames):
        self.collation_started.emit()
        with open(save_file, "w") as collated_file:
            self.process = Process(
                target=_collate, args=(collated_file, filenames,)
            )
            self.process.start()
            self.state = True
            self.process.join()
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
