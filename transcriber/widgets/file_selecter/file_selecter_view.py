import os

from PyQt5 import QtCore, QtWidgets
from transcriber.widgets import SearchableList

FLOAT_END = " (Float).DAT"
TAG_END = " (Tagname).DAT"


class FileSelecterView(QtWidgets.QWidget):
    files_added = QtCore.pyqtSignal(list)
    files_removed = QtCore.pyqtSignal(list)

    def __init__(self):
        super(FileSelecterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()
        self.names_to_paths = {}

        self.files = SearchableList(self, list_name="Loaded Files")
        self.files.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.load_files = QtWidgets.QPushButton("Load Float File(s)", self)
        self.del_file = QtWidgets.QPushButton("Remove", self)
        self.del_file.setEnabled(False)

        self.load_files.setToolTip(
            "Select float files to transcribe. File names end in '(Float).DAT'."
        )
        self.del_file.setToolTip(
            "Remove selected files. These will no longer be transcribed."
        )

        self.load_files.clicked.connect(self.select_files)
        self.del_file.clicked.connect(self.del_current)
        self.connect_current_changed(self.enable_deletion)
        self.files.doubleClicked.connect(self.del_current)
        self._layout.addWidget(self.load_files)
        self._layout.addWidget(self.files)
        self._layout.addWidget(self.del_file)
        self.setLayout(self._layout)

    def filenames(self):
        return [
            self.names_to_paths[self.files.item(i).text()]
            for i in range(self.files.count())
        ]

    def files_loaded(self):
        return self.files.count()

    def select_files(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self,
            caption="Select Float File(s) - DAT",
            filter="DAT (*Float*.DAT)",  # can't use brackets for some reason
        )
        if filenames:
            self.add_files(filenames)

    def add_files(self, filepaths):
        labels = []
        for filepath in filepaths:
            if filepath.endswith(FLOAT_END):
                folder = os.path.dirname(filepath)
                filename = "".join(
                    os.path.basename(filepath).rsplit(FLOAT_END, 1)
                )

                tag_file_path = filepath.replace(FLOAT_END, TAG_END)

                label = f"{filename} ({folder})"
                if (
                    os.path.exists(tag_file_path)
                    and label not in self.names_to_paths
                ):
                    labels.append(label)
                    self.names_to_paths[label] = (filename, tag_file_path)
        if labels:
            self.files.addItems(labels)
            self.files_added.emit([self.names_to_paths[l] for l in labels])

    def del_current(self):
        names = []
        for item in self.files.selectedItems():
            self.files.takeItem(self.files.row(item))
            names.append(self.names_to_paths[item.text()])
            del self.names_to_paths[item.text()]
        if not self.files.count():
            self.del_file.setEnabled(False)
        self.files_removed.emit(names)

    def enable_deletion(self):
        self.del_file.setEnabled(True)

    def change_drag_drop_state(self, state):
        self.files.change_drag_drop_state(state)

    def sort_items(self, sort_direction):
        self.files.sort_items(sort_direction)

    def connect_files_added(self, slot):
        self.files_added.connect(slot)

    def connect_files_removed(self, slot):
        self.files_removed.connect(slot)

    def connect_current_changed(self, slot):
        self.files.currentItemChanged.connect(slot)
