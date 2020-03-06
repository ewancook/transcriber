from multiprocessing import cpu_count, Pool

class Run:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.total = 0
        self.completed = 0

    def slim(self, filenames, tags):
        self.total, self.completed = len(filenames), 0
        for filename in filenames:
            self.model.convert(filename, tags)
            self.completed += 1
            self.view.update_progress(100*self.completed/self.total)

    def multi_slim(self, filenames, tags):
        self.total, self.completed = len(filenames), 0
        pool = Pool(processes=cpu_count())
        for filename in filenames:
            pool.apply_async(self.model.convert, args=(filename, tags,),callback=self.update_by_one)

    def update_by_one(self, result):
        self.completed += 1
        self.view.update_progress(100*self.completed/self.total)

    @property
    def multithreaded(self):
        return self.view.multithreaded()

    def reset_progress(self):
        self.view.update_progress(0)

    def disable(self):
        self.view.disable()

    def enable(self):
        self.view.enable()

    def connect_run_clicked(self, slot):
        self.view.connect_run_clicked(slot)

    def disconnect_run_clicked(self, slot):
        self.view.disconnect_run_clicked(slot)
