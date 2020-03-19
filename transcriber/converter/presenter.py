from PyQt5 import QtCore

from . import utils


class Converter(QtCore.QObject):
    def __init__(self, view, model):
        super(Converter, self).__init__()
        self.view = view
        self.model = model
        self.connect_conversion_update(self.view.update_progress)

        self.model_thread = QtCore.QThread()
        self.model_thread.start()
        self.model.moveToThread(self.model_thread)

    def convert(self, filenames, tags, total_tags, num_cpu):
        self.model.start.emit(filenames, tags, total_tags, num_cpu)

    @property
    def multithreaded(self):
        return self.view.multithreaded()

    def reset_progress(self):
        self.view.reset_progress()

    def disable_run(self):
        self.view.disable_run()

    def enable_run(self):
        self.view.enable_run()

    def connect_run_clicked(self, slot):
        self.view.connect_run_clicked(slot)

    def disconnect_run_clicked(self, slot):
        self.view.disconnect_run_clicked(slot)

    def connect_conversion_started(self, slot):
        self.model.connect_conversion_started(slot)

    def disconnect_conversion_started(self, slot):
        self.model.disconnect_conversion_started(slot)

    def connect_conversion_finished(self, slot):
        self.model.connect_conversion_finished(slot)

    def disconnect_conversion_finished(self, slot):
        self.model.disconnect_conversion_finished(slot)

    def connect_conversion_error(self, slot):
        self.model.connect_conversion_error(slot)

    def disconnect_conversion_error(self, slot):
        self.model.disconnect_conversion_error(slot)

    def connect_conversion_update(self, slot):
        self.model.connect_conversion_update(slot)

    def disconnect_conversion_update(self, slot):
        self.model.disconnect_conversion_update(slot)
