from PyQt5.QtWidgets import QMessageBox


def create_total_tag_map(filenames_to_tags, tags_in_tag_file, parent=None):
    total_tag_map = {}
    for filename, total_tags in filenames_to_tags:
        try:
            total_tag_map[total_tags].append(filename)
        except KeyError:
            total_tag_map[total_tags] = [filename]
    if len(total_tag_map) == 1 and list(total_tag_map)[0] == tags_in_tag_file:
        return True, filenames_to_tags
    return (
        create_window_differing_tags(
            total_tag_map, tags_in_tag_file, parent=parent
        ),
        filenames_to_tags,
    )


def create_window_differing_tags(total_tag_map, tags_in_tag_file, parent=None):
    text_body = "\n".join(
        [
            "{} file(s) found with {} tags.".format(len(v), k)
            for k, v in total_tag_map.items()
        ]
    )
    text = f"""Differing numbers of tags were found:

The loaded tag file has {tags_in_tag_file} tags.

{text_body}

If all selected tags are present in the loaded files, click OK.
If not, or you are unsure, click Cancel."""

    dialog = QMessageBox(parent)
    dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    dialog.setText(text)
    dialog.setIcon(QMessageBox.Warning)
    dialog.setDetailedText(
        "\n".join(
            [
                "{} tags:\n{}\n".format(t, "\n".join(total_tag_map[t]))
                for t in total_tag_map.keys()
            ]
        )
    )
    return True if dialog.exec_() == QMessageBox.Ok else False


def create_window_error(title, text, *errors, parent=None):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setDetailedText(
        "\n".join(
            ["{}: {}".format(type(e).__name__, e.args[0]) for e in errors]
        )
    )
    msg.show()
