from PyQt5 import QtWidgets, QtCore


class TagSelecterView(QtWidgets.QWidget):
    tag_added = QtCore.pyqtSignal()
    tag_deleted = QtCore.pyqtSignal()

    def __init__(self):
        super(TagSelecterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        self.load = QtWidgets.QPushButton("Load Tag File", self)
        self.tags = QtWidgets.QListWidget(self)
        self.tags.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.used = QtWidgets.QListWidget(self)
        self.used.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.add_tag = QtWidgets.QPushButton("Add", self)
        self.del_tag = QtWidgets.QPushButton("Remove", self)
        self.add_tag.setEnabled(False)
        self.del_tag.setEnabled(False)

        self.tags.itemDoubleClicked.connect(self.add_item)
        self.tags.currentItemChanged.connect(self.enable_addition)

        self.used.itemDoubleClicked.connect(self.del_item)
        self.used.currentItemChanged.connect(self.enable_deletion)

        self.add_tag.clicked.connect(self.add_current)
        self.del_tag.clicked.connect(self.del_current)

        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()

        left.addWidget(QtWidgets.QLabel("All Tags:"))
        left.addWidget(self.tags)
        left.addWidget(self.add_tag)

        right.addWidget(QtWidgets.QLabel("Current Tags:"))
        right.addWidget(self.used)
        right.addWidget(self.del_tag)

        horizontal = QtWidgets.QHBoxLayout()
        horizontal.addLayout(left)
        horizontal.addLayout(right)

        self._layout.addWidget(self.load)
        self._layout.addWidget(QtWidgets.QLabel())
        self._layout.addLayout(horizontal)
        self.setLayout(self._layout)

    def load_tag_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            filter="DAT (*.DAT)")
        return filename

    def add_item(self, item):
        tag = item.text()
        if tag not in self.active_tags():
            self.used.addItem(tag)
        self.tag_added.emit()

    def del_item(self, item):
        self.used.takeItem(self.used.row(item))
        if not self.used.count():
            self.disable_deletion()
        self.tag_deleted.emit()

    def active_tags(self):
        return [self.used.item(i).text() for i in range(self.used.count())]

    def add_current(self):
        for item in self.tags.selectedItems():
            self.add_item(item)

    def del_current(self):
        for item in self.used.selectedItems():
            self.del_item(item)

    def enable_deletion(self):
        self.del_tag.setEnabled(True)

    def disable_deletion(self):
        self.del_tag.setEnabled(False)

    def enable_addition(self):
        self.add_tag.setEnabled(True)

    def disable_addition(self):
        self.add_tag.setEnabled(False)

    def set_all(self, tags):
        self.tags.addItems(tags)

    def clear_all(self):
        self.tags.clear()

    def clear_new(self):
        self.used.clear()

    def connect_load_clicked(self, slot):
        self.load.clicked.connect(slot)

    def disconnect_load_clicked(self, slot):
        self.load.clicked.disconnect(slot)

    def connect_tag_added(self, slot):
        self.tag_added.connect(slot)

    def disconnect_tag_added(self, slot):
        self.tag_added.disconnect(slot)

    def connect_tag_deleted(self, slot):
        self.tag_deleted.connect(slot)

    def disconnect_tag_deleted(self, slot):
        self.tag_deleted.disconnect(slot)
