from itertools import islice, takewhile

from transcriber.dbf.fasterdbf import FasterDBF
from transcriber.dbf.new_parser import Parser

TAG_INDEX = "TTagIndex"


def have_correct_tags(filenames, num_tags, encoding="cp437"):
    parser = Parser(required_fields=[TAG_INDEX])
    for filename in filenames:
        table = FasterDBF(filename, [], encoding=encoding, recfactory=None)
        if (table.header.numrecords / num_tags).is_integer():
            parsed = islice(parser.parse_all(filename), 0, num_tags + 1)
            if len({s[TAG_INDEX] for s in parsed}) == num_tags:
                yield filename


def determine_total_tags(filenames, encoding="cp437"):
    parser = Parser()
    for float_file, tag_file in filenames:
        yield (float_file, sum(1 for _ in parser.parse_tag_file(tag_file)))

        # try:
        #     for row in takewhile(lambda r: r[TAG_INDEX] not in tags, table):
        #         tags.add(row[TAG_INDEX])
        #     yield (float_file, len(tags))
        # except KeyError:
        #     yield (float_file, 0)
