import unittest
from unittest import mock

from transcriber.converter.multiprocessing_model import (
    MultiProcessingConverterModel,
)


class TestMultiProcessingModel(unittest.TestCase):
    def setUp(self):
        self.model = MultiProcessingConverterModel()

    @mock.patch(
        "transcriber.converter.multiprocessing_model.MultiProcessingConverterModel.handle_error"
    )
    @mock.patch(
        "transcriber.converter.multiprocessing_model.create_dbf_worker"
    )
    @mock.patch("transcriber.converter.dbfworker.worker.DBFWorker.convert")
    @mock.patch("multiprocessing.Pool")
    @mock.patch("PyQt5.QtCore.pyqtSignal")
    def test_convert_called_with_right_total_tags(
        self, mock_signal, mock_pool, mock_worker, mock_create, mock_err
    ):
        filenames_to_tags = [
            ("this", 10),
            ("is", 20),
            ("a", 20),
            ("test", 21),
        ]
        tags = ["here", "tags"]
        tag_lookup = ["here", "are", "some", "tags"]
        self.model.convert(
            filenames_to_tags, 1, {"tags": tags, "tag_lookup": tag_lookup}
        )
        self.assertEqual(mock_create.call_count, len(filenames_to_tags))
        mock_create.assert_has_calls(
            [
                mock.call(
                    filename=f[0],
                    tags=tags,
                    total_tags=f[1],
                    tag_lookup=tag_lookup,
                )
                for f in filenames_to_tags
            ]
        )
