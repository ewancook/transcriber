class TagSelecter:
    def __init__(self, view, model):
        self.view = view
        self.model = model

    @property
    def tags(self):
        return self.model.tags

    @property
    def active_tags(self):
        return self.view.active_tags()

    def load_file(self, filename):
        self.model.load(filename)
        self.view.disable_deletion()
        self.view.disable_addition()

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

    def connect_load_clicked(self, slot):
        self.view.connect_load_clicked(slot)

    def disconnect_load_clicked(self, slot):
        self.view.disconnect_load_clicked(slot)

    def connect_tag_added(self, slot):
        self.view.connect_tag_added(slot)

    def disconnect_tag_added(self, slot):
        self.view.disconnect_tag_added(slot)

    def connect_tag_deleted(self, slot):
        self.view.connect_tag_deleted(slot)

    def disconnect_tag_deleted(self, slot):
        self.view.disconnect_tag_deleted(slot)
