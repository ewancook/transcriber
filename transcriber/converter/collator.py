from itertools import islice

from PyQt5 import QtCore

from transcriber.converter.workers import utils


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
    collation_finished = QtCore.pyqtSignal()

    start = QtCore.pyqtSignal(str, list)

    def __init__(self):
        super(Collator, self).__init__()
        self.start.connect(self.collate)

    @QtCore.pyqtSlot(str, list)
    def collate(self, save_file, filenames):
        self.collation_started.emit()
        with open(save_file, "w") as collated_file:
            collate_files(
                collated_file,
                [utils.transcribed_filename(f) for f in filenames],
            )
        self.collation_finished.emit()

    def connect_collation_started(self, slot):
        self.collation_started.connect(slot)

    def disconnect_collation_started(self, slot):
        self.collation_started.disconnect(slot)

    def connect_collation_finished(self, slot):
        self.collation_finished.connect(slot)

    def disconnect_collation_finished(self, slot):
        self.collation_finished.disconnect(slot)
