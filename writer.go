package transcriber

import (
	"fmt"
	"io"
	"strconv"
)

const (
	comma   byte = ','
	newLine byte = '\n'
)

var (
	columnNames = []byte("Date,Time")
	commaSlice  = []byte{comma}
)

// A Writer writes parsed dbase records to an io.Writer.
// The precision of the float64 values and the number of rows to be
// averaged, for data reduction, are specified.
type Writer struct {
	w                     io.Writer
	columns               int
	precision             int
	rowsToAverage         int
	minAverageBufCapacity int
	writeBuffer           []byte
	columnValues          []*float64
	columnIncrementCount  []int
}

// NewWriter returns a new Writer that writes to w.
// The named tags from the dbase database are used to format columns,
// and the float64 precision and the number of rows to be averaged are
// also required.
func NewWriter(w io.Writer, tags [][]byte, precision int) *Writer {
	columns := len(tags)
	minAverageBufCapacity := (precision+4)*columns + 20

	return &Writer{
		w:                     w,
		columns:               columns,
		precision:             precision,
		minAverageBufCapacity: minAverageBufCapacity,
		// Date, (10) + Time, (8) + Comma (columns+1) + Values (precision+3)*columns + NewLine (1)
		writeBuffer:          make([]byte, 0, minAverageBufCapacity),
		columnValues:         make([]*float64, columns),
		columnIncrementCount: make([]int, columns),
	}
}

// WriteRow writes (and formats) a row into the destination io.Writer.
// If a tag is omitted, no value will be written in its respective column.
func (w *Writer) WriteRow(r Row) error {
	buf := w.writeBuffer[:0]
	buf = addDateTime(buf, r.date, r.time)

	// clear the columnValues writeBuffer before use.
	for i := 0; i < len(w.columnValues); i++ {
		w.columnValues[i] = nil
	}

	// set values for columns where a value is present.
	for i := 0; i < len(r.values); i++ {
		w.columnValues[r.values[i].column] = &r.values[i].value
	}

	for i, value := range w.columnValues {
		if i > 0 {
			buf = append(buf, comma)
		}
		if value != nil {
			buf = strconv.AppendFloat(buf, *value, 'f', w.precision, 64)
		}
	}
	buf = append(buf, newLine)
	if _, err := w.w.Write(buf); err != nil {
		return fmt.Errorf("error writing row: %w", err)
	}
	return nil
}

// WriteAveragedRow averages a slice of Row(s) and
// formats and writes these to the destination io.Writer.
//
// If values for certain tags are omitted, the respective
// average for that tag will use fewer values than for other
// tags (n < len(rows)).
func (w *Writer) WriteAveragedRow(rows []Row) error {
	last := len(rows) - 1

	buf := w.writeBuffer[:0]
	buf = addDateTime(buf, rows[last].date, rows[last].time)

	// clear the columnValues writeBuffer before use.
	for i := 0; i < len(w.columnValues); i++ {
		w.columnValues[i] = nil
	}

	// clear the divisors used for calculating the average column value.
	for i := 0; i < len(w.columnIncrementCount); i++ {
		w.columnIncrementCount[i] = 0
	}

	for _, row := range rows {
		for i := 0; i < len(row.values); i++ {
			column := row.values[i].column
			w.columnIncrementCount[column]++

			if w.columnValues[column] != nil {
				*(w.columnValues[column]) += row.values[i].value
				continue
			}
			w.columnValues[column] = &row.values[i].value
		}
	}

	for i, value := range w.columnValues {
		if i > 0 {
			buf = append(buf, comma)
		}
		if value != nil {
			*value /= float64(w.columnIncrementCount[i])
			buf = strconv.AppendFloat(buf, *value, 'f', w.precision, 64)
		}
	}

	buf = append(buf, newLine)
	if _, err := w.w.Write(buf); err != nil {
		return fmt.Errorf("error writing averaged row: %w", err)
	}
	return nil
}

// WriteHeader writes the first row to the destination io.Writer.
// This consists of the headers for each tag and the date and time.
func (w *Writer) WriteHeader(tags [][]byte) error {
	size := len(columnNames) + len(tags) + 1
	for _, t := range tags {
		size += len(t)
	}
	header := make([]byte, 0, size)
	header = append(header, columnNames...)
	for _, t := range tags {
		header = append(header, comma)
		header = append(header, t...)
	}
	header = append(header, newLine)
	if _, err := w.w.Write(header); err != nil {
		return fmt.Errorf("error writing file header: %w", err)
	}
	return nil
}

func addDateTime(dest, date, time []byte) []byte {
	dest = append(dest, date...)
	dest = append(dest, comma)
	dest = append(dest, time...)
	dest = append(dest, comma)
	return dest
}
