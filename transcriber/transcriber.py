from multiprocessing import cpu_count

from transcriber.file_selecter.presenter import FileSelecter
from transcriber.file_selecter.view import FileSelecterView

from transcriber.tag_selecter.presenter import TagSelecter
from transcriber.tag_selecter.view import TagSelecterView
from transcriber.tag_selecter.model import TagSelecterModel

from transcriber.converter.presenter import Converter
from transcriber.converter.view import ConverterView
from transcriber.converter.multithreading_model import MultiThreadingConverterModel
from transcriber.converter.collator import Collator

from PyQt5 import QtWidgets, QtCore


class Transcriber(QtWidgets.QMainWindow):
    def __init__(self):
        super(Transcriber, self).__init__()

        self.file_selecter = FileSelecter(FileSelecterView())
        self.file_selecter.connect_del_clicked(self.check_run)
        self.file_selecter.connect_files_added(self.check_run)

        self.tag_selecter = TagSelecter(TagSelecterView(), TagSelecterModel())
        self.tag_selecter.connect_tag_added(self.check_run)
        self.tag_selecter.connect_tag_deleted(self.check_run)

        self.run_widget = Converter(
            ConverterView(),
            MultiThreadingConverterModel(),
            Collator())
        self.run_widget.connect_run_clicked(self.run_widget.reset_progress)
        self.run_widget.connect_run_clicked(self.convert)
        self.run_widget.connect_conversion_started(self.disable_all)
        self.run_widget.connect_conversion_finished(self.enable_all)
        self.run_widget.connect_conversion_finished(self.collate)

        self.run_widget.connect_conversion_error(print)
        self.run_widget.connect_collation_started(self.disable_all)
        self.run_widget.connect_collation_finished(self.enable_all)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.file_selecter.view)
        self.splitter.addWidget(self.tag_selecter.view)

        self._widget_list = QtWidgets.QVBoxLayout()
        self._widget_list.addWidget(self.splitter)
        self._widget_list.addWidget(self.run_widget.view)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self._widget_list)
        self.setWindowTitle("Transcriber")

    def check_run(self):
        if self.tag_selecter.active_tags and self.file_selecter.filenames:
            self.run_widget.enable_run()
        else:
            self.run_widget.disable_run()

    def convert(self):
        self.run_widget.convert(
            self.file_selecter.filenames,
            set(self.tag_selecter.active_tags),
            len(self.tag_selecter.tags),
            cpu_count() if self.run_widget.multithreaded else 1)

    def collate(self):
        if self.run_widget.collate_files:
            save_file, _ = QtWidgets.QFileDialog.getSaveFileName(
                caption="Select Output File - Collated CSV", filter="CSV (*.csv)")
            if save_file:
                self.run_widget.collate(
                    save_file, self.file_selecter.filenames)

    def disable_all(self):
        self.centralWidget().setEnabled(False)

    def enable_all(self):
        self.centralWidget().setEnabled(True)
