from PyQt5 import QtWidgets, QtCore


class FileSelecterView(QtWidgets.QWidget):
    files_added = QtCore.pyqtSignal()

    def __init__(self):
        super(FileSelecterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        self.files = QtWidgets.QListWidget(self)
        self.files.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.add_file = QtWidgets.QPushButton("Load CSV File(s)", self)
        self.del_file = QtWidgets.QPushButton("Remove", self)
        self.del_file.setEnabled(False)

        self.connect_add_clicked(self.load_csv)
        self.connect_del_clicked(self.del_current)
        self.connect_current_changed(self.enable_deletion)
        self.files.doubleClicked.connect(self.del_current)

        self._layout.addWidget(self.add_file)
        self._layout.addWidget(QtWidgets.QLabel())
        self._layout.addWidget(QtWidgets.QLabel("Loaded:"))
        self._layout.addWidget(self.files)
        self._layout.addWidget(self.del_file)
        self.setLayout(self._layout)

    def filenames(self):
        return [self.files.item(i).text() for i in range(self.files.count())]

    def load_csv(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            filter="CSV (*.csv)")
        if filenames:
            self.add_files(filenames)
            self.files_added.emit()

    def add_files(self, files):
        self.files.addItems([f for f in files if f not in self.filenames()])

    def del_current(self):
        for item in self.files.selectedItems():
            self.files.takeItem(self.files.row(item))
        if not self.files.count():
            self.del_file.setEnabled(False)

    def enable_deletion(self):
        self.del_file.setEnabled(True)

    def connect_files_added(self, slot):
        self.files_added.connect(slot)

    def disconnect_files_added(self, slot):
        self.files_added.disconnect(slot)

    def connect_add_clicked(self, slot):
        self.add_file.clicked.connect(slot)

    def disconnect_add_clicked(self, slot):
        self.add_file.clicked.disconnect(slot)

    def connect_del_clicked(self, slot):
        self.del_file.clicked.connect(slot)

    def disconnect_del_clicked(self, slot):
        self.del_file.clicked.disconnect(slot)

    def connect_current_changed(self, slot):
        self.files.currentItemChanged.connect(slot)

    def disconnect_current_changed(self, slot):
        self.files.currentItemChanged.disconnect(slot)
