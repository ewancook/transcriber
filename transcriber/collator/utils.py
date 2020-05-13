from itertools import islice

from transcriber.converter.dbfworker import utils


def collate(save_file, filenames):
    collate_files(
        save_file, [utils.transcribed_filename(f) for f in filenames],
    )
    save_file.close()  # parent won't close this, so we have to


def collate_files(collated_file, filenames):
    with open(filenames[0], "r") as file_with_headers:
        append_file_to_collated(collated_file, file_with_headers)
    for filename in filenames[1:]:
        with open(filename, "r") as file_to_append:
            file_data = islice(file_to_append, 1, None)
            append_file_to_collated(collated_file, file_data)


def append_file_to_collated(collated_file, file_to_append):
    for line in file_to_append:
        collated_file.write(line)
    collated_file.write("\n")
