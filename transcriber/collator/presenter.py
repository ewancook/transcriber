from PyQt5 import QtCore


class Collator:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        self.model_thread = QtCore.QThread()
        self.model_thread.start()
        self.model.moveToThread(self.model_thread)

    def collate(self, filenames):
        self.model.start.emit(self.view.collated_file, filenames)

    @property
    def collate_files(self):
        return self.view.collate_files()

    def emit_terminate_collation(self):
        self.model.terminate_collation.emit()

    def disable_view(self):
        self.view.setEnabled(False)

    def enable_view(self):
        self.view.setEnabled(True)

    def connect_collation_started(self, slot):
        self.model.connect_collation_started(slot)

    def connect_collation_finished(self, slot):
        self.model.connect_collation_finished(slot)
