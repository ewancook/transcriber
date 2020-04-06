from PyQt5 import QtCore

from transcriber.converter.workers import worker


class ConverterWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)


class ThreadedWorker(QtCore.QRunnable):
    def __init__(self):
        super(ThreadedWorker, self).__init__()
        self.signals = ConverterWorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            self.convert()
        except Exception as e:
            self.signals.error.emit((self.filename, e))
        self.signals.finished.emit()

    def connect_finished(self, slot):
        self.signals.finished.connect(slot, QtCore.Qt.DirectConnection)

    def disconnect_finished(self, slot):
        self.signals.finished.disconnect(slot)

    def connect_error(self, slot):
        self.signals.error.connect(slot, QtCore.Qt.DirectConnection)

    def disconnect_error(self, slot):
        self.signals.error.disconnect(slot)


class ThreadedCSVWorker(worker.CSVWorker, ThreadedWorker):
    def __init__(self, filename, tags, tag_lookup):
        worker.CSVWorker.__init__(self, filename, tags, tag_lookup)
        ThreadedWorker.__init__(self)


class ThreadedDBFWorker(worker.DBFWorker, ThreadedWorker):
    def __init__(self, filename, tags, tag_lookup):
        worker.DBFWorker.__init__(self, filename, tags, tag_lookup)
        ThreadedWorker.__init__(self)
