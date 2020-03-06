from PyQt5 import QtWidgets, QtCore

class TagSelecterView(QtWidgets.QWidget):
    def __init__(self):
        super(TagSelecterView, self).__init__()

        self._layout = QtWidgets.QVBoxLayout()

        self.load = QtWidgets.QPushButton("Load Tag File", self)
        self.tags = QtWidgets.QListWidget(self)
        self.used = QtWidgets.QListWidget(self)
        self.add_tag = QtWidgets.QPushButton("Add", self)
        self.del_tag = QtWidgets.QPushButton("Remove", self)
        self.add_tag.setEnabled(False)
        self.del_tag.setEnabled(False)

        self.connect_add_clicked(self.add_current)
        self.connect_del_clicked(self.del_current)
        self.connect_current_all_changed(self.enable_addition)
        self.connect_current_new_changed(self.enable_deletion)

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

        self.setWindowTitle("Select Tags")
        self.setLayout(self._layout)

    def active_tags(self):
        return [self.used.item(i).text() for i in range(self.used.count())]

    def add_current(self):
        tag = self.tags.item(self.tags.currentRow())
        self.used.addItem(tag.text())

    def del_current(self):
        self.used.takeItem(self.used.currentRow())
        if not self.used.count():
                self.del_tag.setEnabled(False)

    def disable(self):
        self.add_tag.setEnabled(False)
        self.del_tag.setEnabled(False)
        self.load.setEnabled(False)
        self.tags.setEnabled(False)
        self.used.setEnabled(False)

    def enable(self):
        self.add_tag.setEnabled(True)
        self.del_tag.setEnabled(True)
        self.load.setEnabled(True)
        self.tags.setEnabled(True)
        self.used.setEnabled(True)

    def enable_deletion(self):
        self.del_tag.setEnabled(True)

    def enable_addition(self):
        self.add_tag.setEnabled(True)

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

    def connect_add_clicked(self, slot):
        self.add_tag.clicked.connect(slot)

    def disconnect_add_clicked(self, slot):
        self.add_tag.clicked.disconnect(slot)

    def connect_del_clicked(self, slot):
        self.del_tag.clicked.connect(slot)

    def disconnect_del_clicked(self, slot):
        self.del_tag.clicked.disconnect(slot)

    def connect_current_all_changed(self, slot):
        self.tags.currentItemChanged.connect(slot)

    def disconnect_current_all_changed(self, slot):
        self.tags.currentItemChanged.disconnect(slot)

    def connect_current_new_changed(self, slot):
        self.used.currentItemChanged.connect(slot)

    def disconnect_current_new_changed(self, slot):
        self.used.currentItemChanged.disconnect(slot)
