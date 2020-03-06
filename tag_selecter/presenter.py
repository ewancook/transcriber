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

    def show(self):
        self.view.show()

    def load_file(self, filename):
        self.model.load(filename)

    def add_tag(self):
        self.view.add_tag()

    def del_current(self):
        self.view.del_current()

    def disable(self):
        self.view.disable()

    def enable(self):
        self.view.enable()

    def enable_deletion(self):
        self.view.enable_deletion()

    def enable_addition(self):
        self.view.enable_addition()

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

    def connect_add_clicked(self, slot):
        self.view.connect_add_clicked(slot)

    def disconnect_add_clicked(self, slot):
        self.view.disconnect_add_clicked(slot)

    def connect_del_clicked(self, slot):
        self.view.connect_del_clicked(slot)

    def disconnect_del_clicked(self, slot):
        self.view.disconnect_del_clicked(slot)

    def connect_current_all_changed(self, slot):
        self.view.connect_current_all_changed(slot)

    def disconnect_current_all_changed(self, slot):
        self.view.disconnect_current_all_changed(slot)

    def connect_current_new_changed(self, slot):
        self.view.connect_current_new_changed(slot)

    def disconnect_current_new_changed(self, slot):
        self.view.disconnect_current_new_changed(slot)
