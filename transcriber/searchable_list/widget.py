from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView


class SearchableListWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, list_name=""):
        super(SearchableListWidget, self).__init__(parent)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_text = (
            f"Search {list_name} ({{}})" if list_name else "Search ({}):"
        )
        self.search_bar.setPlaceholderText(self.search_text.format("0"))
        self.search_bar.textChanged.connect(self._update_list)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSortingEnabled(True)
        self.itemDoubleClicked = self.list_widget.itemDoubleClicked
        self.currentItemChanged = self.list_widget.currentItemChanged
        self.doubleClicked = self.list_widget.doubleClicked

        vertical = QtWidgets.QVBoxLayout()
        vertical.addWidget(self.search_bar)
        vertical.addWidget(self.list_widget)
        self.setLayout(vertical)

    def setSelectionMode(self, *args, **kwargs):
        self.list_widget.setSelectionMode(*args, **kwargs)

    def update_search_text(func):
        def wraps(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.search_bar.setPlaceholderText(
                self.search_text.format(self.count())
            )

        return wraps

    @update_search_text
    def clear(self, *args, **kwargs):
        self.list_widget.clear(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self.list_widget.count(*args, **kwargs)

    @update_search_text
    def addItem(self, *args, **kwargs):
        self.list_widget.addItem(*args, **kwargs)

    @update_search_text
    def addItems(self, *args, **kwargs):
        self.list_widget.addItems(*args, **kwargs)

    def item(self, *args, **kwargs):
        return self.list_widget.item(*args, **kwargs)

    def selectedItems(self, *args, **kwargs):
        return self.list_widget.selectedItems(*args, **kwargs)

    @update_search_text
    def takeItem(self, *args, **kwargs):
        return self.list_widget.takeItem(*args, **kwargs)

    def row(self, *args, **kwargs):
        return self.list_widget.row(*args, **kwargs)

    def change_drag_drop_state(self, state=False):
        self.list_widget.setDragDropMode(
            QAbstractItemView.InternalMove
            if state
            else QAbstractItemView.NoDragDrop
        )

    def sort_items(self, sort_direction):
        self.list_widget.sortItems(sort_direction)

    def _update_list(self, text):
        text = text.lower()
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(text not in item.text().lower())
