import io
import tempfile
import unittest
from unittest import mock

from transcriber.converter import collator
from transcriber.converter.workers.utils import transcribed_filename

file_contents = """Date,Time,Tag
01/01/1970,00:00:00,0.01
01/01/1970,00:00:08,0.02
01/01/1970,00:00:16,0.03"""


class TestCollator(unittest.TestCase):
    def _fake_process(self, target=None, args=[]):
        collator._collate(args[0], args[1])
        return None

    @mock.patch("multiprocessing.Process.__init__", new=_fake_process)
    @mock.patch("multiprocessing.Process.join")
    @mock.patch("multiprocessing.Process.start")
    @mock.patch("transcriber.converter.collator.collate_files")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_collator_collate(
        self, mock_file, collate_files, mock_start, mock_join
    ):
        save_file = "this/is/the/collated/file.csv"
        filenames = ["this/is/a/test.csv"]
        collator.Collator().collate(save_file, filenames)
        collate_files.assert_called_with(
            mock_file(), [transcribed_filename(f) for f in filenames]
        )
        mock_start.assert_called_once()
        mock_join.assert_called_once()

    @mock.patch("transcriber.converter.collator.collate_files")
    def test__collate(self, mock_collate):
        save_file = "this/is/the/collated/file.csv"
        filenames = ["this/is/a/test.csv"]
        collator._collate(save_file, filenames)
        mock_collate.assert_called_with(
            save_file, [transcribed_filename(f) for f in filenames]
        )

    def test_collate_files(self):
        num_files = 3
        files = [
            tempfile.NamedTemporaryFile(delete=False) for i in range(num_files)
        ]
        for f in files:
            f.write(file_contents.encode())
            f.close()
        collated_file = io.StringIO()
        collator.collate_files(collated_file, [f.name for f in files])
        collated_file.seek(0)
        file_contents_body = "\n".join(file_contents.split("\n")[2:])
        self.assertEqual(
            collated_file.read(),
            "\n".join(
                [
                    file_contents,
                    *[file_contents_body for i in range(num_files - 1)],
                    "",
                ]
            ),
        )

    def test_append_file_to_collated_initially_empty(self):
        collated_file = io.StringIO()
        file_to_append = io.StringIO(file_contents)
        collator.append_file_to_collated(collated_file, file_to_append)
        collated_file.seek(0)
        self.assertEqual(collated_file.read(), f"{file_contents}\n")
        file_to_append.seek(0)
        collator.append_file_to_collated(collated_file, file_to_append)
        collated_file.seek(0)
        self.assertEqual(
            collated_file.read(), "\n".join([file_contents, file_contents, ""])
        )
