from PyQt5 import QtCore, QtWidgets


class CollatorView(QtWidgets.QWidget):
    def __init__(self):
        super(CollatorView, self).__init__()

        self.collated_file = None
        self.collate = QtWidgets.QCheckBox("Collate Output (Overall CSV)")
        self.collate.setChecked(False)
        self.collate.setToolTip(
            "If enabled, an additional CSV containing all data will be produced. Files are collated in order of appearance (see 'Loaded')."
        )
        self.collate.stateChanged.connect(self.select_collated_file)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self.collate)
        self.setLayout(self._layout)

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
