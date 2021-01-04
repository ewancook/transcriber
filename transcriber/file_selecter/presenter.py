class FileSelecter:
    def __init__(self, view):
        self.view = view

    @property
    def filenames(self):
        return self.view.filenames()

    @property
    def files_loaded(self):
        return self.view.files_loaded()

    def add_files(self, files):
        self.view.add_files(files)

    def del_current(self, file):
        self.view.del_current()

    def enable_deletion(self):
        self.view.enable_deletion()

    def disable_view(self):
        self.view.setEnabled(False)

    def enable_view(self):
        self.view.setEnabled(True)

    def change_drag_drop_state(self, state):
        self.view.change_drag_drop_state(state)

    def sort_items(self, sort_direction):
        self.view.sort_items(sort_direction)

    def connect_files_added(self, slot):
        self.view.connect_files_added(slot)

    def connect_files_removed(self, slot):
        self.view.connect_files_removed(slot)

    def connect_current_changed(self, slot):
        self.view.connect_current_changed(slot)
