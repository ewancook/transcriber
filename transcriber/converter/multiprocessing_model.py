from multiprocessing import Pool

from PyQt5 import QtCore

from transcriber.converter import model
from transcriber.converter.workers.worker import DBFWorker


class MultiProcessingConverterModel(model.ConverterModel):
    def __init__(self):
        super(MultiProcessingConverterModel, self).__init__()
        self.successful_conversions = []
        self.exceptions = []
        self.pool = None

    @QtCore.pyqtSlot(list, set, int, list)
    def convert(self, filenames, tags, num_cpu, tag_lookup):
        self.successful_conversions = []
        self.exceptions = []
        self.pool = Pool(processes=num_cpu)
        self.total_files = len(filenames)
        self.conversion_started.emit()
        for filename in filenames:
            worker = DBFWorker(filename, tags, tag_lookup)
            self.pool.apply_async(
                func=worker.work,
                callback=self.register_successful_conversion,
                error_callback=self.handle_error,
            )
        self.pool.close()
        self.pool.join()
        unsuccessful = [
            f for f in filenames if f not in self.successful_conversions
        ]
        for file, error in zip(unsuccessful, self.exceptions):
            self.conversion_error.emit((file, error))
        self.conversion_finished.emit()

    @QtCore.pyqtSlot()
    def terminate(self):
        self.pool.terminate()
        self.conversion_finished.emit()

    def register_successful_conversion(self, filename):
        self.successful_conversions.append(filename)
        self.update_conversion_total()

    def handle_error(self, error):
        self.exceptions.append(error)
        self.update_conversion_total()
