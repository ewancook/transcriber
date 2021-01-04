class TagSelecter:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.tags = set()

    @property
    def tag_lookups(self):
        return self.model.tags

    @property
    def active_tags(self):
        return self.view.active_tags()

    def load_files(self, filenames):
        self.model.load(filenames)
        self.update_tags()

    def remove_file_tags(self, filenames):
        self.model.remove_file_tags(filenames)
        self.update_tags()

    def update_tags(self):
        if len(self.tags):
            self.clear_all()
        if not len(self.tag_lookups):
            self.tags.clear()
        else:
            self.tags = set.intersection(
                *[
                    set([t for t in self.tag_lookups[k]])
                    for k, v in self.tag_lookups.items()
                ]
            )
            self.set_all(self.tags)
        self.clear_invalid_selection(self.tags)

    def add_tag(self):
        self.view.add_tag()

    def del_current(self):
        self.view.del_current()

    def enable_deletion(self):
        self.view.enable_deletion()

    def disable_deletion(self):
        self.view.disable_deletion()

    def enable_addition(self):
        self.view.enable_addition()

    def disable_addition(self):
        self.view.disable_addition()

    def set_all(self, tags):
        self.view.set_all(tags)

    def clear_all(self):
        self.view.clear_all()

    def clear_new(self):
        self.view.clear_new()

    def clear_invalid_selection(self, new_tags):
        self.view.clear_invalid_selection(new_tags)

    def disable_view(self):
        self.view.setEnabled(False)

    def enable_view(self):
        self.view.setEnabled(True)

    def connect_load_clicked(self, slot):
        self.view.connect_load_clicked(slot)

    def connect_tag_added(self, slot):
        self.view.connect_tag_added(slot)

    def connect_tag_deleted(self, slot):
        self.view.connect_tag_deleted(slot)

    def connect_loading_error(self, slot):
        self.model.connect_loading_error(slot)

    def connect_loading_finished(self, slot):
        self.model.connect_loading_finished(slot)
