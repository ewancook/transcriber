from transcriber.dbf.parser import Parser

from PyQt5 import QtCore


class TagSelecterModel(QtCore.QObject):
    loading_error = QtCore.pyqtSignal(Exception)

    def __init__(self):
        super(TagSelecterModel, self).__init__()
        self.tags = []
        self.parser = Parser(["Tagname"])

    def load(self, filename):
        try:
            self.tags = [r["Tagname"].decode().strip()
                         for r in self.parser.parse_file(filename)]
        except Exception as e:
            self.loading_error.emit(e)

    def connect_loading_error(self, slot):
        self.loading_error.connect(slot)

    def disconnect_loading_error(self, slot):
        self.loading_error.disconnect(slot)
