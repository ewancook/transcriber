import sys

from file_selecter.presenter import FileSelecter
from file_selecter.view import FileSelecterView

from PyQt5 import QtCore, QtGui, QtWidgets

class SlimCSV(QtWidgets.QMainWindow):
    def __init__(self):
        super(SlimCSV, self).__init__()

        self.setWindowTitle("SlimCSV")
        self._widget_list = QtWidgets.QVBoxLayout()

        self.file_selecter = FileSelecter(FileSelecterView())
        self.file_selecter.connect_add_clicked(self.load_csv)
        self.file_selecter.connect_del_clicked(self.file_selecter.del_current)
        self.file_selecter.connect_current_changed(self.file_selecter.enable_deletion)

        self.progress = QtWidgets.QProgressBar(self)

        self._widget_list.addWidget(self.file_selecter.view)
        self._widget_list.addWidget(QtWidgets.QLabel())
        self._widget_list.addWidget(self.progress)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self._widget_list)

    def load_csv(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames()
        self.file_selecter.add_files(filenames)

    def del_item(self):
        item = self.file_selecter.del_current()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    slim_csv = SlimCSV()
    slim_csv.show()
    sys.exit(app.exec_())
