import logging
import os

from PyQt5.QtWidgets import QMessageBox


def create_total_tag_map(filenames_to_tags):
    total_tag_map = {}
    for filename, total_tags in filenames_to_tags:
        try:
            total_tag_map[total_tags].append(filename)
        except KeyError:
            total_tag_map[total_tags] = [filename]
    return total_tag_map


def get_out_of_range_tags(total_tag_map, tags_in_tag_file, selected_tags):
    tag_lookup = [tags_in_tag_file.index(i) for i in selected_tags]
    files = {}
    for index in tag_lookup:
        affected_files = [
            v for k, v in total_tag_map.items() if k < index or not k
        ]
        if len(affected_files):
            files[tags_in_tag_file[index]] = [
                f for l in affected_files for f in l
            ]
    return files


def create_invalid_tags_error(invalid_tags, parent=None):
    text = f"""Some tags are not present in all loaded files.
\nPlease refer to the log and remove the affected files or tags."""
    for tag, files in invalid_tags.items():
        logging.error(f"{tag} is not present in:")
        for _file in files:
            logging.error(f"\t{os.path.basename(_file)}")
    return create_dialog(text, parent=parent, title="Invalid Tags")


def create_dialog(text, detail=None, title=None, parent=None):
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(text)
    dialog.setIcon(QMessageBox.Warning)
    if detail is not None:
        dialog.setDetailedText(detail)
    return True if dialog.exec_() == QMessageBox.Ok else False
