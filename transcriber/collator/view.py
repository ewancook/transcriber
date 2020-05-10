from PyQt5 import QtCore, QtWidgets


class CollatorView(QtWidgets.QWidget):
    sorting_state_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        super(CollatorView, self).__init__()

        self.collated_file = None
        self.collate = QtWidgets.QCheckBox("Collate Output")
        self.collate.setChecked(False)
        self.collate.setToolTip(
            "If enabled, an additional CSV containing all data will be produced. Files are collated in order of appearance (see 'Loaded')."
        )
        self.collate.stateChanged.connect(self.change_main_option_states)
        self.collate.stateChanged.connect(self.select_collated_file)

        self.set_sorting = QtWidgets.QCheckBox("Sort by Name")
        self.set_sorting.stateChanged.connect(self.change_sorting_type_state)
        self.set_sorting.stateChanged.connect(self.maybe_emit_sorting_signal)
        self.set_sorting.setEnabled(False)
        self.sorting_type = QtWidgets.QComboBox()
        self.sorting_type.setEnabled(False)
        self.sorting_type.addItems(["Ascending", "Descending"])
        self.sorting_type.currentIndexChanged.connect(
            self.sorting_state_changed.emit
        )
        self.drag_drop = QtWidgets.QCheckBox("Drag to Rearrange Files")
        self.drag_drop.setEnabled(False)
        self.drag_drop.stateChanged.connect(self.change_sorting_state)

        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(QtWidgets.QLabel("Collation Options:"), 0, 0, 1, 2)
        self.grid.addWidget(self.collate, 1, 0, 1, 2)
        self.grid.addWidget(self.set_sorting, 2, 0)
        self.grid.addWidget(self.sorting_type, 2, 1)
        self.grid.addWidget(self.drag_drop, 3, 0, 1, 2)

        self.setLayout(self.grid)

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

    def collate_files(self):
        return self.collate.isChecked()

    def change_main_option_states(self, state):
        self.set_sorting.setEnabled(state)
        self.drag_drop.setEnabled(state)

    def change_sorting_type_state(self, state):
        self.sorting_type.setEnabled(state)

    def maybe_emit_sorting_signal(self, state):
        if state:
            self.sorting_state_changed.emit(self.sorting_type.currentIndex())
            self.drag_drop.setCheckState(QtCore.Qt.Unchecked)

    def change_sorting_state(self, state):
        if state:
            self.set_sorting.setCheckState(QtCore.Qt.Unchecked)

    def connect_sorting_state_changed(self, slot):
        self.sorting_state_changed.connect(slot)

    def connect_drag_drop_state_changed(self, slot):
        self.drag_drop.stateChanged.connect(slot)
