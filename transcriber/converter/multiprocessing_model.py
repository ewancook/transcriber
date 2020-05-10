from multiprocessing import Pool

from PyQt5 import QtCore

from transcriber.converter import model
from transcriber.converter.dbfworker.worker import DBFWorker

TERMINATE = 2


def create_dbf_worker(filename, tags, tag_lookup, total_tags):
    return DBFWorker(filename, tags, tag_lookup, total_tags)


class MultiProcessingConverterModel(model.ConverterModel):
    def __init__(self):
        super(MultiProcessingConverterModel, self).__init__()
        self.exceptions = []
        self.pool = None

    @QtCore.pyqtSlot(list, set, int, list)
    def convert(self, filenames_to_tags, tags, num_cpu, tag_lookup):
        self.exceptions = []
        self.pool = Pool(processes=num_cpu)
        self.conversion_started.emit()
        for filename, total_tags in filenames_to_tags:
            worker = create_dbf_worker(
                filename, tags, tag_lookup, total_tags=total_tags
            )
            self.pool.apply_async(
                func=worker.work,
                callback=self.update_conversion_total_success,
                error_callback=self.handle_error,
            )
        self.pool.close()
        self.pool.join()
        for error in self.exceptions:
            self.conversion_error.emit(error)
        self.conversion_finished.emit(self.pool._state != TERMINATE)

    @QtCore.pyqtSlot()
    def terminate(self):
        self.pool.terminate()

    def update_conversion_total_success(self, filename):
        self.update_conversion_total()

    def handle_error(self, error):
        self.exceptions.append(error)
        self.update_conversion_total()
