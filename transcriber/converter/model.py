from PyQt5 import QtCore

from . import utils


class ConverterModel(QtCore.QObject):
    conversion_started = QtCore.pyqtSignal()
    conversion_finished = QtCore.pyqtSignal()
    conversion_error = QtCore.pyqtSignal(Exception)
    conversion_update = QtCore.pyqtSignal(float)

    start = QtCore.pyqtSignal(list, list, int, int)

    def __init__(self):
        super(ConverterModel, self).__init__()
        self.pool = QtCore.QThreadPool()
        self.total_files = 0
        self.start.connect(self.convert)

    @QtCore.pyqtSlot(list, list, int, int)
    def convert(self, filenames, tags, total_tags, num_cpu):
        self.total_files = len(filenames)
        self.conversion_started.emit()
        self.pool.setMaxThreadCount(num_cpu)
        for filename in filenames:
            worker = utils.create_worker(filename, tags, total_tags)
            worker.connect_finished(self.update_conversion_total)
            worker.connect_error(self.conversion_error.emit)
            self.pool.start(worker)
        self.pool.waitForDone()
        self.conversion_finished.emit()

    def update_conversion_total(self):
        self.conversion_update.emit(1 / self.total_files)

    def connect_conversion_started(self, slot):
        self.conversion_started.connect(slot)

    def disconnect_conversion_started(self, slot):
        self.conversion_started.disconnect(slot)

    def connect_conversion_finished(self, slot):
        self.conversion_finished.connect(slot)

    def disconnect_conversion_finished(self, slot):
        self.conversion_finished.disconnect(slot)

    def connect_conversion_error(self, slot):
        self.conversion_error.connect(slot)

    def disconnect_conversion_error(self, slot):
        self.conversion_error.disconnect(slot)

    def connect_conversion_update(self, slot):
        self.conversion_update.connect(slot)

    def disconnect_conversion_update(self, slot):
        self.conversion_update.disconnect(slot)
