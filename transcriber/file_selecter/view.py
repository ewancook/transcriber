import os

from PyQt5 import QtCore, QtWidgets
from transcriber.searchable_list.widget import SearchableListWidget

FLOAT_END = " (Float).DAT"
TAG_END = " (Tagname).DAT"


class FileSelecterView(QtWidgets.QWidget):
    files_added = QtCore.pyqtSignal(list)
    files_removed = QtCore.pyqtSignal(list)

    def __init__(self):
        super(FileSelecterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()
        self.names_to_paths = {}

        self.files = SearchableListWidget(self, list_name="Loaded Files")
        self.files.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.load_folder = QtWidgets.QPushButton("Load Folder", self)
        self.del_file = QtWidgets.QPushButton("Remove", self)
        self.del_file.setEnabled(False)

        self.load_folder.setToolTip(
            "Select a folder containing files to transcribe. It should include file names ending in '(Float).DAT' and '(Tagname).DAT'."
        )
        self.del_file.setToolTip(
            "Remove selected files. These will no longer be transcribed."
        )

        self.load_folder.clicked.connect(self.select_folder)
        self.del_file.clicked.connect(self.del_current)
        self.connect_current_changed(self.enable_deletion)
        self.files.doubleClicked.connect(self.del_current)
        self._layout.addWidget(self.load_folder)
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

    def select_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Load Folder",
        )
        if folder:
            self.folder = os.path.basename(folder)
            self.add_files(folder)

    def add_files(self, folder):
        labels = []
        filenames = os.listdir(folder)
        for filename in filenames:
            if filename.endswith(FLOAT_END):
                name = "".join(filename.rsplit(FLOAT_END, 1))
                tag_file = f"{name}{TAG_END}"
                label = f"{name} ({self.folder})"
                if tag_file in filenames and label not in self.names_to_paths:
                    labels.append(label)
                    self.names_to_paths[label] = (
                        os.path.join(folder, filename),
                        os.path.join(folder, tag_file),
                    )
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
