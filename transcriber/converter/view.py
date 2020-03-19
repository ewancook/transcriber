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

        self.run = QtWidgets.QPushButton("Run", self)
        self.run.setEnabled(False)

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setValue(0)

        self._layout.addWidget(self.multi)
        self._layout.addWidget(self.run)
        self._layout.addWidget(self.progress)

        self.setLayout(self._layout)

    def multithreaded(self):
        return self.multi.isChecked()

    def enable_run(self):
        self.run.setEnabled(True)

    def disable_run(self):
        self.run.setEnabled(False)

    def reset_progress(self):
        self.progress.setValue(0)

    def update_progress(self, increment):
        self.progress.setValue(self.progress.value() + 100 * increment)

    def connect_run_clicked(self, slot):
        self.run.clicked.connect(slot)

    def disconnect_run_clicked(self, slot):
        self.run.clicked.disconnect(slot)
