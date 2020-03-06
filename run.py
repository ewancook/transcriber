import sys
import multiprocessing

from file_selecter.presenter import FileSelecter
from file_selecter.view import FileSelecterView

from tag_selecter.presenter import TagSelecter
from tag_selecter.view import TagSelecterView
from tag_selecter.model import TagSelectorModel

from run.presenter import Run
from run.view import RunView
from run.model import RunModel

import PyQt5

from PyQt5 import QtCore, QtGui, QtWidgets

class SlimCSV(QtWidgets.QMainWindow):
    def __init__(self):
        super(SlimCSV, self).__init__()

        self.tags_complete = False
        self.csv_complete = False

        self.setWindowTitle("SlimCSV")
        self._widget_list = QtWidgets.QVBoxLayout()

        self.file_selecter = FileSelecter(FileSelecterView())
        self.file_selecter.connect_add_clicked(self.load_csv)

        self.tag_selecter = TagSelecter(TagSelecterView(), TagSelectorModel())
        self.tag_selecter.connect_load_clicked(self.load_tag_file)

        self.load = QtWidgets.QPushButton("Load CSV File(s)")
        self.load.clicked.connect(self.file_selecter.show)

        self.tags = QtWidgets.QPushButton("Select Tags")
        self.tags.clicked.connect(self.tag_selecter.show)

        self.run = Run(RunView(), RunModel())
        self.run.connect_run_clicked(self.run.reset_progress)
        self.run.connect_run_clicked(self.slim)

        self.file_selecter.connect_add_clicked(self.run.reset_progress)
        self.file_selecter.connect_del_clicked(self.run.reset_progress)
        self.file_selecter.connect_current_changed(self.run.reset_progress)
        self.tag_selecter.connect_add_clicked(self.run.reset_progress)
        self.tag_selecter.connect_del_clicked(self.run.reset_progress)
        self.tag_selecter.connect_load_clicked(self.run.reset_progress)
        self.tag_selecter.connect_current_new_changed(self.run.reset_progress)
        self.tag_selecter.connect_current_all_changed(self.run.reset_progress)

        self._widget_list.addWidget(self.load)
        self._widget_list.addWidget(self.tags)
        self._widget_list.addWidget(QtWidgets.QLabel())
        self._widget_list.addWidget(self.run.view)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self._widget_list)

    def load_csv(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames()
        if filenames is not None:
            self.file_selecter.add_files(filenames)
            self.csv_complete = True
            self.check_run()

    def load_tag_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filename is not None:
            self.tag_selecter.load_file(filename)
            self.tag_selecter.clear_all()
            self.tag_selecter.clear_new()
            tags = self.tag_selecter.tags
            if tags is not None:
                self.tag_selecter.set_all(tags)
                self.tags_complete = True
                self.check_run()

    def check_run(self):
        if self.tags_complete and self.csv_complete:
            self.run.enable()

    def slim(self):
        self.disable_all()
        self.setEnabled(False)
        self.update()
        filenames = self.file_selecter.filenames
        tags = self.tag_selecter.active_tags
        if self.run.multithreaded:
            self.run.multi_slim(filenames, tags)
        else:
            self.run.slim(filenames, tags)
        self.enable_all()
        self.setEnabled(True)

    def enable_all(self):
        self.file_selecter.enable()
        self.tag_selecter.enable()
        self.run.enable()
        self.tags.setEnabled(True)
        self.load.setEnabled(True)

    def disable_all(self):
        self.file_selecter.disable()
        self.tag_selecter.disable()
        self.run.disable()
        self.tags.setEnabled(False)
        self.load.setEnabled(False)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QtWidgets.QApplication([])
    slim_csv = SlimCSV()
    slim_csv.show()
    sys.exit(app.exec_())
