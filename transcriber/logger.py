import logging

from PyQt5 import QtCore, QtWidgets


class Logger(logging.Handler, QtWidgets.QWidget):
    append_plain_text = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(Logger, self).__init__()
        QtWidgets.QWidget.__init__(self, parent)

        self.text_edit = QtWidgets.QPlainTextEdit(parent)
        self.text_edit.setReadOnly(True)

        self.append_plain_text.connect(self.text_edit.appendPlainText)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self.text_edit)
        self.setLayout(self._layout)

    def emit(self, record):
        msg = self.format(record)
        self.append_plain_text.emit(msg)
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )
