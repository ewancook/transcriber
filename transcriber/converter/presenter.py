from PyQt5 import QtCore

from transcriber.converter.utils import determine_total_tags


class Converter(QtCore.QObject):
    def __init__(self, view, model, collator):
        super(Converter, self).__init__()
        self.view = view
        self.model = model
        self.collator = collator
        self.connect_conversion_update(self.view.update_progress)

        self.model_thread = QtCore.QThread()
        self.model_thread.start()
        self.model.moveToThread(self.model_thread)

        self.collator.moveToThread(self.model_thread)

        self.connect_conversion_started(self.view.set_running)
        self.connect_collation_started(self.view.set_running)
        self.connect_collation_started(self.view.set_progress_collating)

        self.connect_conversion_finished(self.handle_conversion_finished)
        self.connect_collation_finished(self.handle_collation_finished)

        self.connect_cancel_clicked(self.model.terminate_work.emit)
        self.connect_cancel_clicked(self.collator.terminate_collation.emit)

    def handle_conversion_finished(self, successful):
        if not successful:
            self.reset_progress()
        self.view.set_finished()  # must always set_finished() because there may be conversion errors

    def handle_collation_finished(self, successful):
        if successful:
            self.view.set_progress_finished()
        else:
            self.reset_progress()
        self.view.set_finished()

    def convert(self, filenames_to_tags, tags, num_cpu, tag_lookup):
        self.view.set_progress_range(0, len(filenames_to_tags))
        if not isinstance(tags, set):
            tags = set(tags)
        self.model.start.emit(filenames_to_tags, tags, num_cpu, tag_lookup)

    def collate(self, filenames):
        self.collator.start.emit(self.view.collated_file, filenames)

    def determine_total_tags(self, filenames):
        return determine_total_tags(filenames)

    @property
    def multithreaded(self):
        return self.view.multithreaded()

    @property
    def collate_files(self):
        return self.view.collate_files()

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

    def connect_collation_started(self, slot):
        self.collator.connect_collation_started(slot)

    def connect_collation_finished(self, slot):
        self.collator.connect_collation_finished(slot)
