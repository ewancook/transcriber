package transcriber

import (
	"bytes"
	"fmt"
	"io"
	"strconv"

	"github.com/ewancook/transcriber/dbf"
)

var (
	ignoredFloatFields = [3]string{"Internal", "Status", "Millitm"}
	ignoredTagFields   = [2]string{"TagType", "TagDataTyp"}
)

// Row represents a parsed row in a DBF file. The date is formatted as "DD/MM/YYYY" and the time is formattd as "HH:MM:SS".
type Row struct {
	date, time []byte
	values     []Datum
}

// Datum represents a single datapoint for a specific tag in a row.
type Datum struct {
	column int
	value  float64
}

// Tags represent the tags in a tag file. This includes the names and ordered indices included in th file.
type Tags struct {
	indices []int
	names   map[int]string
}

// ParseTagFile parses a DBF tag file into a *Tags.
func ParseTagFile(r io.ReadSeeker) (*Tags, error) {
	reader, err := dbf.NewReader(r)
	if err != nil {
		return nil, fmt.Errorf("failed to create reader: %w", err)
	}
	reader.IgnoreFields(ignoredTagFields[:]...)

	tags := &Tags{
		indices: make([]int, reader.NumRecords),
		names:   make(map[int]string),
	}

	for i := 0; i < int(reader.NumRecords); i++ {
		record, err := reader.Read()
		if err != nil {
			return nil, fmt.Errorf("failed to read into record: %w", err)
		}

		if len(record) != 2 {
			return nil, fmt.Errorf("tag file misstructured: %v records per row", len(record))
		}

		for r := 0; r < len(record); r++ {
			record[r] = bytes.TrimSpace(record[r])
		}

		name := string(record[0])
		index, err := strconv.Atoi(string(record[1]))
		if err != nil {
			return nil, fmt.Errorf("tag file misstructured; failed to convert listed tag indices: %w", err)
		}

		tags.indices[i] = index
		tags.names[index] = name
	}
	return tags, nil
}
