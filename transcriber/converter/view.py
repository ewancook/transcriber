import multiprocessing

from PyQt5 import QtCore, QtWidgets


class ConverterView(QtWidgets.QWidget):
    run_clicked = QtCore.pyqtSignal()
    cancel_clicked = QtCore.pyqtSignal()

    def __init__(self):
        super(ConverterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        cores = multiprocessing.cpu_count()
        self.multi = QtWidgets.QCheckBox(
            "Parallel Conversion ({} Cores)".format(cores), self
        )
        self.multi.setChecked(True)
        self.multi.setToolTip(
            "If enabled, all CPU cores are used to transcribe multiple files simultaneously."
        )

        self.collated_file = None
        self.collate = QtWidgets.QCheckBox("Collate Output (Overall CSV)")
        self.collate.setChecked(False)
        self.collate.setToolTip(
            "If enabled, an additional CSV containing all data will be produced. Files are collated in order of appearance (see 'Loaded')."
        )
        self.collate.stateChanged.connect(self.select_collated_file)

        self.run = QtWidgets.QPushButton("Run", self)
        self.run.clicked.connect(self.emit_run_or_cancel)
        self.run.setEnabled(False)
        self.running = False

        self.run.setToolTip(
            "Transcribe the loaded files using the selected tags.\n\nTranscribed files are created in the same directories as the original files and have the format:\n\t'ORIGINAL_NAME (Transcribed).csv'"
        )

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setValue(0)
        self.progress_value = 0

        horizontal_layout = QtWidgets.QHBoxLayout()
        horizontal_layout.addWidget(self.multi)
        horizontal_layout.addWidget(self.collate)

        self._layout.addLayout(horizontal_layout)
        self._layout.addWidget(self.run)
        self._layout.addWidget(self.progress)

        self.setLayout(self._layout)

    def multithreaded(self):
        return self.multi.isChecked()

    def collate_files(self):
        return self.collate.isChecked()

    def enable_run(self):
        self.run.setEnabled(True)

    def disable_run(self):
        self.run.setEnabled(False)

    def reset_progress(self):
        self.progress.setFormat("%p%")
        self.progress_value = 0
        self.progress.reset()

    def set_progress_range(self, min, max):
        self.progress.setRange(min, max)

    def update_progress(self):
        self.progress_value += 1
        self.progress.setValue(self.progress_value)

    def set_progress_finished(self):
        self.progress.setFormat("%p%")
        self.progress.setValue(self.progress.maximum())

    def set_progress_collating(self):
        self.progress.setFormat("Collating")

    def set_running(self):
        self.running = True
        self.run.setText("Cancel")

    def set_finished(self):
        self.running = False
        self.run.setText("Run")

    def emit_run_or_cancel(self):
        if self.running:
            self.cancel_clicked.emit()
        else:
            self.run_clicked.emit()

    def _change_state_of_widgets_except_run(self, state):
        self.progress.setEnabled(state)
        self.multi.setEnabled(state)
        self.collate.setEnabled(state)

    def disable_view_except_run(self):
        self._change_state_of_widgets_except_run(False)

    def select_collated_file(self, state):
        if not state:
            return
        collated_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption="Select Output File - Collated CSV",
            filter="CSV (*.csv)",
        )
        if not collated_file:
            self.collate.setCheckState(QtCore.Qt.Unchecked)
        self.collated_file = collated_file

    def enable_view_except_run(self):
        self._change_state_of_widgets_except_run(True)

    def connect_run_clicked(self, slot):
        self.run_clicked.connect(slot)

    def disconnect_run_clicked(self, slot):
        self.run_clicked.disconnect(slot)

    def connect_cancel_clicked(self, slot):
        self.cancel_clicked.connect(slot)

    def disconnect_cancel_clicked(self, slot):
        self.cancel_clicked.disconnect(slot)
