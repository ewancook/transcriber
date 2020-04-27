from PyQt5 import QtWidgets


class SearchableListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, search_text="Search"):
        super(SearchableListWidget, self).__init__(parent)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText(search_text)
        self.search_bar.textChanged.connect(self._update_list)

        self.list_widget = QtWidgets.QListWidget()
        self.itemDoubleClicked = self.list_widget.itemDoubleClicked
        self.currentItemChanged = self.list_widget.currentItemChanged
        self.doubleClicked = self.list_widget.doubleClicked

        vertical = QtWidgets.QVBoxLayout()
        vertical.addWidget(self.search_bar)
        vertical.addWidget(self.list_widget)
        self.setLayout(vertical)

    def setSelectionMode(self, *args, **kwargs):
        self.list_widget.setSelectionMode(*args, **kwargs)

    def clear(self, *args, **kwargs):
        self.list_widget.clear(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self.list_widget.count(*args, **kwargs)

    def addItem(self, *args, **kwargs):
        self.list_widget.addItem(*args, **kwargs)

    def addItems(self, *args, **kwargs):
        self.list_widget.addItems(*args, **kwargs)

    def item(self, *args, **kwargs):
        return self.list_widget.item(*args, **kwargs)

    def selectedItems(self, *args, **kwargs):
        return self.list_widget.selectedItems(*args, **kwargs)

    def takeItem(self, *args, **kwargs):
        return self.list_widget.takeItem(*args, **kwargs)

    def row(self, *args, **kwargs):
        return self.list_widget.row(*args, **kwargs)

    def _update_list(self, text):
        text = text.lower()
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(text not in item.text().lower())
