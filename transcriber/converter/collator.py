from itertools import islice

from PyQt5 import QtCore

from transcriber.converter import utils


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
        with open(save_file, "w") as collated:
            with open(utils.transcribed_filename(filenames[0])) as f:
                for line in f:
                    collated.write(line)
            for filename in filenames[1:]:
                collated.write("\n")
                with open(utils.transcribed_filename(filename), "r") as f:
                    for line in islice(f, 2, None):
                        collated.write(line)
        self.collation_finished.emit()

    def connect_collation_started(self, slot):
        self.collation_started.connect(slot)

    def disconnect_collation_started(self, slot):
        self.collation_started.disconnect(slot)

    def connect_collation_finished(self, slot):
        self.collation_finished.connect(slot)

    def disconnect_collation_finished(self, slot):
        self.collation_finished.disconnect(slot)
