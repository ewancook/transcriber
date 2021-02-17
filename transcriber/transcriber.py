import logging

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
from transcriber.widgets import (
    FileSelecter,
    FileSelecterView,
    TagSelecter,
    TagSelecterModel,
    TagSelecterView,
)


class Transcriber(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Transcriber, self).__init__(parent)

        self.file_selecter = FileSelecter(FileSelecterView())
        self.file_selecter.connect_files_removed(self.check_run)
        self.file_selecter.connect_files_removed(self.remove_file_tags)
        self.file_selecter.connect_files_added(self.load_tag_files)
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
        self.collator.connect_sorting_state_changed(
            self.file_selecter.sort_items
        )
        self.collator.connect_drag_drop_state_changed(
            self.file_selecter.change_drag_drop_state
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

        options = QtWidgets.QVBoxLayout()
        options.addWidget(self.collator.view)
        options.addWidget(self.converter.view)

        self._widget_list = QtWidgets.QHBoxLayout()
        self._widget_list.addWidget(self.splitter)
        self._widget_list.addLayout(options)

        self.setLayout(self._widget_list)

    def check_run(self):
        if self.tag_selecter.active_tags and self.file_selecter.files_loaded:
            self.converter.enable_run()
        else:
            self.converter.disable_run()

    def remove_file_tags(self, filenames):
        self.tag_selecter.remove_file_tags(f[1] for f in filenames)

    def load_tag_files(self, filenames):
        self.tag_selecter.load_files(set(f[1] for f in filenames))

    def convert(self):
        self.converter.reset_progress()
        self.disable_all()
        filenames_to_tags = self.get_filenames_to_tags(
            self.file_selecter.filenames,
            self.tag_selecter.tags,
            self.tag_selecter.active_tags,
        )
        self.enable_all()
        if filenames_to_tags is not None:
            self.converter.convert(
                filenames_to_tags,
                self.tag_selecter.active_tags,
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
            self.collator.collate([f[0] for f in self.file_selecter.filenames])

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

    def get_filenames_to_tags(self, filenames, tags, active_tags):
        filenames_to_tags = list(
            self.converter.determine_total_tags(filenames)
        )
        total_tag_map = utils.create_total_tag_map(filenames_to_tags)
        if len(total_tag_map) == 1 and list(total_tag_map)[0] == len(tags):
            return filenames_to_tags
        out_of_range_tags = utils.get_out_of_range_tags(
            total_tag_map, tags, active_tags
        )
        if len(out_of_range_tags):
            utils.create_invalid_tags_error(out_of_range_tags)
            return None
        return filenames_to_tags

    def _handle_tag_loading_error(self, error):
        text = """Tags could not be parsed from this file.
\nPlease refer to the log for the full error."""
        utils.create_dialog(text, title="Error Loading Tag file", parent=self)
        logging.error(
            f"Failed to parse tag file: {type(error).__name__} ({error})"
        )

    def _handle_conversion_errors(self):
        if self.conversion_errors:
            failed = len(self.conversion_errors)
            text = f"""{failed} file(s) could not be converted.\n
Refer to the log for a complete list of files and errors."""
            utils.create_dialog(text, title="Conversion Error(s)")
            self.conversion_errors = []
