import multiprocessing

from PyQt5 import QtCore, QtWidgets


class ConverterView(QtWidgets.QWidget):
    run_clicked = QtCore.pyqtSignal()
    cancel_clicked = QtCore.pyqtSignal()

    def __init__(self):
        super(ConverterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        cores = multiprocessing.cpu_count()
        self.multi = QtWidgets.QCheckBox("Parallel Conversion (Cores)", self)
        self.multi.setChecked(True)
        self.multi.stateChanged.connect(self.change_multi_spinbox_state)
        self.multi.setToolTip(
            "If enabled, multiple CPU cores are used to transcribe multiple files simultaneously."
        )
        self.multi_spin = QtWidgets.QSpinBox()
        self.multi_spin.setRange(1, cores)
        self.multi_spin.setValue(cores)

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

        self.set_rounding = QtWidgets.QCheckBox("Set Decimal Places")
        self.set_rounding.stateChanged.connect(
            self.change_rounding_spinbox_state
        )
        self.rounding_spin = QtWidgets.QSpinBox()
        self.rounding_spin.setEnabled(False)

        self.default_rounding = 8
        self.rounding_spin.setValue(self.default_rounding)
        self.rounding_spin.setRange(0, 16)

        self.average_rows = QtWidgets.QCheckBox("Average every 'N' Rows")
        self.average_rows.setToolTip(
            "If enabled, every 'N' rows are combined to give average values for each tag. The initial date and time are used."
        )
        self.average_rows.stateChanged.connect(
            self.change_average_rows_spinbox_state
        )
        self.average_rows_spin = QtWidgets.QSpinBox()
        self.average_rows_spin.setEnabled(False)
        self.average_rows_spin.setMinimum(2)

        self.options_label = QtWidgets.QLabel("Conversion Options:")

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.options_label, 0, 0, 1, 2)
        self.grid.addWidget(self.average_rows, 1, 0)
        self.grid.addWidget(self.average_rows_spin, 1, 1)
        self.grid.addWidget(self.set_rounding, 2, 0)
        self.grid.addWidget(self.rounding_spin, 2, 1)
        self.grid.addWidget(self.multi, 3, 0)
        self.grid.addWidget(self.multi_spin, 3, 1)
        self.grid.addWidget(self.run, 4, 0, 1, 2)
        self.grid.addWidget(self.progress, 5, 0, 1, 2)

        self.setLayout(self.grid)

    @property
    def num_cores(self):
        return int(self.multi_spin.value()) if self.multi.isChecked() else 1

    @property
    def num_decimal_places(self):
        return (
            int(self.rounding_spin.value())
            if self.set_rounding.isChecked()
            else self.default_rounding
        )

    @property
    def rows_to_average(self):
        return (
            int(self.average_rows_spin.value())
            if self.average_rows.isChecked()
            else None
        )

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
        self.average_rows.setEnabled(state)
        self.average_rows_spin.setEnabled(
            state if self.average_rows.isChecked() else False
        )
        self.set_rounding.setEnabled(state)
        self.rounding_spin.setEnabled(
            state if self.set_rounding.isChecked() else False
        )
        self.multi_spin.setEnabled(state if self.multi.isChecked() else False)
        self.options_label.setEnabled(state)

    def disable_view_except_run(self):
        self._change_state_of_widgets_except_run(False)

    def enable_view_except_run(self):
        self._change_state_of_widgets_except_run(True)

    def change_rounding_spinbox_state(self, state):
        self.rounding_spin.setEnabled(state)

    def change_average_rows_spinbox_state(self, state):
        self.average_rows_spin.setEnabled(state)

    def change_multi_spinbox_state(self, state):
        self.multi_spin.setEnabled(state)

    def connect_run_clicked(self, slot):
        self.run_clicked.connect(slot)

    def connect_cancel_clicked(self, slot):
        self.cancel_clicked.connect(slot)
