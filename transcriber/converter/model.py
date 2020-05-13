from PyQt5 import QtCore


class ConverterModel(QtCore.QObject):
    conversion_started = QtCore.pyqtSignal()
    conversion_finished = QtCore.pyqtSignal(bool)
    conversion_error = QtCore.pyqtSignal(Exception)
    conversion_update = QtCore.pyqtSignal()
    terminate_work = QtCore.pyqtSignal()

    start = QtCore.pyqtSignal(list, int, dict)

    def __init__(self):
        super(ConverterModel, self).__init__()
        self.start.connect(self.convert)
        self.terminate_work.connect(self.terminate, QtCore.Qt.DirectConnection)

    def update_conversion_total(self):
        self.conversion_update.emit()

    def connect_conversion_started(self, slot):
        self.conversion_started.connect(slot)

    def connect_conversion_finished(self, slot):
        self.conversion_finished.connect(slot)

    def connect_conversion_error(self, slot):
        self.conversion_error.connect(slot)

    def connect_conversion_update(self, slot):
        self.conversion_update.connect(slot)
