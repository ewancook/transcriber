from itertools import islice, takewhile

from transcriber.dbf.parser import Parser, SubclassedDBF

TAG_INDEX = "TagIndex"


def have_correct_tags(filenames, num_tags, encoding="cp437"):
    parser = Parser(required_fields=[TAG_INDEX])
    for filename in filenames:
        table = SubclassedDBF(filename, [], encoding=encoding, recfactory=None)
        if (table.header.numrecords / num_tags).is_integer():
            parsed = islice(parser.parse_all(filename), 0, num_tags + 1)
            if len({s[TAG_INDEX] for s in parsed}) == num_tags:
                yield filename


def determine_total_tags(filenames, encoding="cp437"):
    parser = Parser(required_fields=[TAG_INDEX])
    for filename in filenames:
        tags = set()
        table = parser.parse_all(filename)
        try:
            for row in takewhile(lambda r: r[TAG_INDEX] not in tags, table):
                tags.add(row[TAG_INDEX])
            yield (filename, len(tags))
        except KeyError:
            yield (filename, 0)
