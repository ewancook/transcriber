from PyQt5 import QtCore

from transcriber.dbf.parser import Parser


class TagSelecterModel(QtCore.QObject):
    loading_error = QtCore.pyqtSignal(Exception)
    loading_finished = QtCore.pyqtSignal()

    def __init__(self):
        super(TagSelecterModel, self).__init__()
        self.tags = []
        self.parser = Parser(["Tagname"])

    def load(self, filename):
        self.tags = []
        try:
            self.tags = [
                r["Tagname"].decode().strip()
                for r in self.parser.parse_all(filename)
            ]
        except Exception as e:
            self.loading_error.emit(e)
        self.loading_finished.emit()

    def connect_loading_error(self, slot):
        self.loading_error.connect(slot)

    def connect_loading_finished(self, slot):
        self.loading_finished.connect(slot)
