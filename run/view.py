import multiprocessing

from PyQt5 import QtWidgets

class RunView(QtWidgets.QWidget):
    def __init__(self):
        super(RunView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        cores = multiprocessing.cpu_count()
        self.multi = QtWidgets.QCheckBox("Multi Threaded ({} Cores)".format(cores), self)
        self.multi.setChecked(True)

        self.run = QtWidgets.QPushButton("Run", self)
        self.run.setEnabled(False)

        self.progress = QtWidgets.QProgressBar(self)

        self._layout.addWidget(self.multi)
        self._layout.addWidget(self.run)
        self._layout.addWidget(self.progress)

        self.setLayout(self._layout)

    def disable(self):
        self.run.setEnabled(False)

    def enable(self):
        self.run.setEnabled(True)

    def multithreaded(self):
        return self.multi.isChecked()

    def update_progress(self, progress):
        self.progress.setValue(progress)

    def connect_run_clicked(self, slot):
        self.run.clicked.connect(slot)

    def disconnect_run_clicked(self, slot):
        self.run.clicked.disconnect(slot)
