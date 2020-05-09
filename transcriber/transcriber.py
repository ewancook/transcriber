from multiprocessing import cpu_count

from PyQt5 import QtCore, QtWidgets

from transcriber.collator.collator import Collator
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

        self.converter = Converter(
            ConverterView(), MultiProcessingConverterModel(), Collator()
        )

        self.conversion_errors = []
        self.converter.connect_run_clicked(self.converter.reset_progress)
        self.converter.connect_run_clicked(self.convert)
        self.converter.connect_conversion_started(self.disable_all)
        self.converter.connect_conversion_finished(
            self._enable_if_errors_or_no_collation
        )
        self.converter.connect_conversion_finished(self.collate)
        self.converter.connect_conversion_finished(
            self._handle_conversion_errors
        )

        self.converter.connect_conversion_error(self._append_conversion_error)

        self.converter.connect_collation_started(self.disable_all)
        self.converter.connect_collation_finished(self.enable_all)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.file_selecter.view)
        self.splitter.addWidget(self.tag_selecter.view)

        self._widget_list = QtWidgets.QVBoxLayout()
        self._widget_list.addWidget(self.splitter)
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
        self.disable_all()
        run, filenames_to_tags = self._run_with_differing_tags(
            self.file_selecter.filenames, len(self.tag_selecter.tags)
        )
        self.enable_all()
        if not run:
            return
        self.converter.convert(
            filenames_to_tags,
            self.tag_selecter.active_tags,
            cpu_count() if self.converter.multithreaded else 1,
            self.tag_selecter.tags,
        )

    def collate(self, successful):
        if not successful:
            self.enable_all()
        elif self.converter.collate_files and not len(self.conversion_errors):
            self.converter.collate(self.file_selecter.filenames)

    def disable_all(self):
        self.file_selecter.disable_view()
        self.tag_selecter.disable_view()
        self.converter.disable_view_except_run()

    def _enable_if_errors_or_no_collation(self):
        if not self.converter.collate_files or len(self.conversion_errors):
            self.enable_all()

    def enable_all(self):
        self.file_selecter.enable_view()
        self.tag_selecter.enable_view()
        self.converter.enable_view_except_run()

    def _append_conversion_error(self, error):
        self.conversion_errors.append(error)

    def _run_with_differing_tags(self, filenames, tags_in_tag_file):
        total_tag_map = {}
        filenames_to_tags = list(
            self.converter.determine_total_tags(filenames)
        )
        for filename, total_tags in filenames_to_tags:
            try:
                total_tag_map[total_tags].append(filename)
            except KeyError:
                total_tag_map[total_tags] = [filename]
        if (
            len(total_tag_map) == 1
            and list(total_tag_map)[0] == tags_in_tag_file
        ):
            return True, filenames_to_tags
        return (
            self._create_window_differing_tags(
                total_tag_map, tags_in_tag_file
            ),
            filenames_to_tags,
        )

    def _create_window_differing_tags(self, total_tag_map, tags_in_tag_file):
        text_body = "\n".join(
            [
                "{} file(s) found with {} tags.".format(len(v), k)
                for k, v in total_tag_map.items()
            ]
        )
        text = f"""Differing numbers of tags were found:

The loaded tag file has {tags_in_tag_file} tags.

{text_body}

If all selected tags are present in the loaded files, click OK.
If not, or you are unsure, click Cancel."""

        dialog = QtWidgets.QMessageBox()
        dialog.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        dialog.setText(text)
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.setDetailedText(
            "\n".join(
                [
                    "{} tags:\n{}\n".format(t, "\n".join(total_tag_map[t]))
                    for t in total_tag_map.keys()
                ]
            )
        )
        return True if dialog.exec_() == QtWidgets.QMessageBox.Ok else False

    def _create_window_error(self, title, text, *errors):
        msg = QtWidgets.QMessageBox(parent=self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setDetailedText(
            "\n".join(
                ["{}: {}".format(type(e).__name__, e.args[0]) for e in errors]
            )
        )
        msg.show()

    def _handle_tag_loading_error(self, error):
        self._create_window_error(
            "Error Loading Tagfile",
            "Tagnames could not be parsed from this file.",
            error,
        )

    def _handle_conversion_errors(self):
        if self.conversion_errors:
            files = "\n".join([i[0] for i in self.conversion_errors])
            self._create_window_error(
                "Conversion Error(s)",
                f"The following files could not be converted:\n\n{files}",
                *[i[1] for i in self.conversion_errors],
            )
            self.conversion_errors = []
