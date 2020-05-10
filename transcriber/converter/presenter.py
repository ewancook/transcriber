from PyQt5 import QtCore

from transcriber.converter.utils import determine_total_tags


class Converter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.connect_conversion_update(self.view.update_progress)

        self.model_thread = QtCore.QThread()
        self.model_thread.start()
        self.model.moveToThread(self.model_thread)

        self.connect_conversion_started(self.view.set_running)
        self.connect_conversion_finished(self.handle_conversion_finished)
        self.connect_cancel_clicked(self.model.terminate_work.emit)

    def handle_conversion_finished(self, successful):
        if not successful:
            self.reset_progress()
        self.view.set_finished()  # must always set_finished() because there may be conversion errors

    def convert(self, filenames_to_tags, tags, num_cpu, tag_lookup):
        self.view.set_progress_range(0, len(filenames_to_tags))
        if not isinstance(tags, set):
            tags = set(tags)
        self.model.start.emit(filenames_to_tags, tags, num_cpu, tag_lookup)

    def determine_total_tags(self, filenames):
        return determine_total_tags(filenames)

    @property
    def multithreaded(self):
        return self.view.multithreaded()

    def reset_progress(self):
        self.view.reset_progress()

    def disable_run(self):
        self.view.disable_run()

    def enable_run(self):
        self.view.enable_run()

    def disable_view_except_run(self):
        self.view.disable_view_except_run()

    def enable_view_except_run(self):
        self.view.enable_view_except_run()

    def set_running(self):
        self.view.set_running()

    def set_finished(self):
        self.view.set_finished()

    def set_progress_collating(self):
        self.view.set_progress_collating()

    def set_progress_finished(self):
        self.view.set_progress_finished()

    def connect_run_clicked(self, slot):
        self.view.connect_run_clicked(slot)

    def connect_cancel_clicked(self, slot):
        self.view.connect_cancel_clicked(slot)

    def connect_conversion_started(self, slot):
        self.model.connect_conversion_started(slot)

    def connect_conversion_finished(self, slot):
        self.model.connect_conversion_finished(slot)

    def connect_conversion_error(self, slot):
        self.model.connect_conversion_error(slot)

    def connect_conversion_update(self, slot):
        self.model.connect_conversion_update(slot)
