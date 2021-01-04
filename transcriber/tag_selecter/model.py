from PyQt5 import QtCore
from transcriber.dbf.new_parser import Parser


class TagSelecterModel(QtCore.QObject):
    loading_error = QtCore.pyqtSignal(Exception)
    loading_finished = QtCore.pyqtSignal()

    def __init__(self):
        super(TagSelecterModel, self).__init__()
        self.tags = {}
        self.parser = Parser()

    def load(self, filenames):
        for filename in filenames:
            try:
                self.tags[filename] = [
                    r["Tagname"].decode().strip()
                    for r in self.parser.parse_tag_file(filename)
                ]
            except Exception as e:
                self.loading_error.emit(e)
        self.loading_finished.emit()

    def remove_file_tags(self, filenames):
        for filename in filenames:
            del self.tags[filename]

    def connect_loading_error(self, slot):
        self.loading_error.connect(slot)

    def connect_loading_finished(self, slot):
        self.loading_finished.connect(slot)
