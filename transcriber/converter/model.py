from PyQt5 import QtCore


class ConverterModel(QtCore.QObject):
    conversion_started = QtCore.pyqtSignal()
    conversion_finished = QtCore.pyqtSignal()
    conversion_error = QtCore.pyqtSignal(tuple)
    conversion_update = QtCore.pyqtSignal()

    start = QtCore.pyqtSignal(list, set, int, list)

    def __init__(self):
        super(ConverterModel, self).__init__()
        self.total_files = 0
        self.start.connect(self.convert)

    def update_conversion_total(self):
        self.conversion_update.emit()

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
