import multiprocessing

from PyQt5 import QtWidgets


class ConverterView(QtWidgets.QWidget):
    def __init__(self):
        super(ConverterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        cores = multiprocessing.cpu_count()
        self.multi = QtWidgets.QCheckBox(
            "Multi Threaded ({} Cores)".format(cores), self)
        self.multi.setChecked(True)

        self.collate = QtWidgets.QCheckBox("Collate Output (Overall CSV)")
        self.collate.setChecked(False)
        self.collate.setToolTip(
            "'Collate Output' produces an additional CSV that includes all data. Files are collated in selection order (see 'Loaded').")

        self.run = QtWidgets.QPushButton("Run", self)
        self.run.setEnabled(False)

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
        self.progress_value = 0
        self.progress.reset()

    def update_progress(self, increment):
        self.progress_value += increment
        self.progress.setValue(self.progress_value * 100)

    def connect_run_clicked(self, slot):
        self.run.clicked.connect(slot)

    def disconnect_run_clicked(self, slot):
        self.run.clicked.disconnect(slot)
