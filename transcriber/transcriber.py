from multiprocessing import cpu_count

from PyQt5 import QtCore, QtWidgets

from transcriber import utils
from transcriber.collator.model import CollatorModel
from transcriber.collator.presenter import Collator
from transcriber.collator.view import CollatorView
from transcriber.converter.multiprocessing_model import (
    MultiProcessingConverterModel,
)
from transcriber.converter.presenter import Converter
from transcriber.converter.view import ConverterView
from transcriber.file_selecter.presenter import FileSelecter
from transcriber.file_selecter.view import FileSelecterView
from transcriber.tag_selecter.model import TagSelecterModel
from transcriber.tag_selecter.presenter import TagSelecter
from transcriber.tag_selecter.view import TagSelecterView

VERSION = "{TRAVIS_TAG}"


class Transcriber(QtWidgets.QMainWindow):
    def __init__(self):
        super(Transcriber, self).__init__()

        self.file_selecter = FileSelecter(FileSelecterView())
        self.file_selecter.connect_files_removed(self.check_run)
        self.file_selecter.connect_files_added(self.check_run)

        self.tag_selecter = TagSelecter(TagSelecterView(), TagSelecterModel())
        self.tag_selecter.connect_tag_added(self.check_run)
        self.tag_selecter.connect_tag_deleted(self.check_run)
        self.tag_selecter.connect_loading_error(self._handle_tag_loading_error)
        self.tag_selecter.connect_loading_finished(self.check_run)

        self.collator = Collator(CollatorView(), CollatorModel())

        self.converter = Converter(
            ConverterView(), MultiProcessingConverterModel()
        )

        self.conversion_errors = []
        self.collator.connect_collation_started(self.converter.set_running)
        self.collator.connect_collation_started(
            self.converter.set_progress_collating
        )
        self.collator.connect_collation_finished(
            self.handle_collation_finished
        )

        self.converter.connect_cancel_clicked(
            self.collator.emit_terminate_collation
        )
        self.converter.connect_run_clicked(self.convert)
        self.converter.connect_conversion_started(self.disable_all)
        self.converter.connect_conversion_finished(self.collate)
        self.converter.connect_conversion_finished(
            self._handle_conversion_errors
        )
        self.converter.connect_conversion_error(self._append_conversion_error)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.file_selecter.view)
        self.splitter.addWidget(self.tag_selecter.view)

        self._widget_list = QtWidgets.QVBoxLayout()
        self._widget_list.addWidget(self.splitter)
        self._widget_list.addWidget(self.collator.view)
        self._widget_list.addWidget(self.converter.view)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self._widget_list)
        self.setWindowTitle(f"Transcriber {VERSION}")

    def check_run(self):
        if self.tag_selecter.active_tags and self.file_selecter.filenames:
            self.converter.enable_run()
        else:
            self.converter.disable_run()

    def convert(self):
        self.converter.reset_progress()
        self.disable_all()
        run, filenames_to_tags = self._run_with_differing_tags(
            self.file_selecter.filenames, len(self.tag_selecter.tags)
        )
        self.enable_all()
        if run:
            self.converter.convert(
                filenames_to_tags,
                self.tag_selecter.active_tags,
                cpu_count() if self.converter.multithreaded else 1,
                self.tag_selecter.tags,
            )

    def collate(self, successful):
        if (
            not successful
            or not self.collator.collate_files
            or len(self.conversion_errors)
        ):
            self.enable_all()
        else:
            self.collator.collate(self.file_selecter.filenames)

    def handle_collation_finished(self, successful):
        if successful:
            self.converter.set_progress_finished()
        else:
            self.converter.reset_progress()
        self.converter.set_finished()
        self.enable_all()

    def disable_all(self):
        self.file_selecter.disable_view()
        self.tag_selecter.disable_view()
        self.converter.disable_view_except_run()
        self.collator.disable_view()

    def enable_all(self):
        self.file_selecter.enable_view()
        self.tag_selecter.enable_view()
        self.converter.enable_view_except_run()
        self.collator.enable_view()

    def _append_conversion_error(self, error):
        self.conversion_errors.append(error)

    def _run_with_differing_tags(self, filenames, tags_in_tag_file):
        filenames_to_tags = list(
            self.converter.determine_total_tags(filenames)
        )
        return utils.create_total_tag_map(
            filenames_to_tags, tags_in_tag_file, self
        )

    def _handle_tag_loading_error(self, error):
        utils.create_window_error(
            "Error Loading Tagfile",
            "Tagnames could not be parsed from this file.",
            error,
            parent=self,
        )

    def _handle_conversion_errors(self):
        if self.conversion_errors:
            filenames = "\n".join(
                [error.args[0] for error in self.conversion_errors]
            )
            utils.create_window_error(
                "Conversion Error(s)",
                f"The following files could not be converted:\n\n{filenames}",
                *[error.args[1] for error in self.conversion_errors],
                parent=self,
            )
            self.conversion_errors = []
