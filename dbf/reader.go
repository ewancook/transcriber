package dbf

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"io"
)

const (
	recordSep      uint8 = 0x20
	recordEnd      uint8 = 0x1a
	null           uint8 = 0x00
	carriageReturn uint8 = 0xd
	newLine        uint8 = 0x0a
)

// A Record contains the values of all fields for a single record in a dbase file.
type Record [][]byte

// A Header contains the values of all elements in the header of a dbase file.
type Header struct {
	Version      uint8
	Year         uint8
	Month        uint8
	Day          uint8
	NumRecords   uint32
	HeaderLength uint16
	RecordLength uint16
}

// A Reader reads records from a dbase file.
type Reader struct {
	Header
	Fields       []Field
	r            io.ReadSeeker
	activeFields int
}

// NewReader returns a new Reader that reads from r.
func NewReader(r io.ReadSeeker) (*Reader, error) {
	buf := make([]byte, 12, 18) // Capacity of 18 allows reuse for Field parsing.
	if _, err := r.Read(buf); err != nil {
		return nil, fmt.Errorf("invalid header format: %w", err)
	}
	header := Header{
		Version:      buf[0],
		Year:         buf[1],
		Month:        buf[2],
		Day:          buf[3],
		NumRecords:   binary.LittleEndian.Uint32(buf[4:8]),
		HeaderLength: binary.LittleEndian.Uint16(buf[8:10]),
		RecordLength: binary.LittleEndian.Uint16(buf[10:12]),
	}
	if _, err := r.Seek(20, io.SeekCurrent); err != nil {
		return nil, fmt.Errorf("invalid header format: %w", err)
	}
	buf = buf[:cap(buf)] // Extend to reuse for Field parsing.

	numFields := (header.HeaderLength - 33) / 32
	fields := make([]Field, numFields)

	for i := range fields {
		if _, err := r.Read(buf); err != nil {
			return nil, fmt.Errorf("invalid field format: %w", err)
		}
		fields[i] = Field{
			Name:     string(bytes.TrimRight(buf[:11], string(null))),
			Type:     FieldType(buf[11]),
			Length:   buf[16],
			Decimals: buf[17],
			active:   true,
		}
		if _, err := r.Seek(14, io.SeekCurrent); err != nil {
			return nil, fmt.Errorf("invalid field format: %w", err)
		}
	}
	if _, err := r.Seek(int64(header.HeaderLength), io.SeekStart); err != nil {
		return nil, fmt.Errorf("incorrect header length: %w", err)
	}
	return &Reader{
		Header:       header,
		Fields:       fields,
		r:            r,
		activeFields: int(numFields),
	}, nil
}

// NewRecord creates a new blank Record with the active fields.
func (r *Reader) NewRecord() Record {
	record := make(Record, 0, r.activeFields)
	for _, field := range r.Fields {
		if field.active {
			record = append(record, make([]byte, field.Length))
		}
	}
	return record
}

// Read reads the next record from r.
func (r *Reader) Read() (Record, error) {
	record := r.NewRecord()
	return record, r.ReadInto(record)
}

// ReadInto reads the next from r into the destination Record.
func (r *Reader) ReadInto(dst Record) error {
	if err := r.readSep(); err != nil {
		return fmt.Errorf("error reading record: %w", err)
	}
	i := 0
	for _, field := range r.Fields {
		if field.active {
			if _, err := r.r.Read(dst[i]); err != nil {
				return fmt.Errorf("error reading fields: %w", err)
			}
			i++
		} else {
			if _, err := r.r.Seek(int64(field.Length), io.SeekCurrent); err != nil {
				return fmt.Errorf("error reading fields: %w", err)
			}
		}

	}
	return nil
}

// Skip skips i records ahead of the current position.
func (r *Reader) Skip(i uint32) error {
	if _, err := r.r.Seek(int64(i)*int64(r.RecordLength), io.SeekCurrent); err != nil {
		return fmt.Errorf("error skipping record: %w", err)
	}
	return nil
}

// IgnoreFields ignores the Fields with the specified names.
// This means they won't be included in Records when using Read, ReadInto, ReadAll.
//
// NewRecord should be used to obtain a new Record after calling, if necessary.
func (r *Reader) IgnoreFields(names ...string) {
	r.setFieldActive(false, names)
}

// ActivateFields activates the Fields with the specified names.
// This means they will be included in Records when using Read, ReadInto, ReadAll.
//
// NewRecord should be used to obtain a new Record after calling, if necessary.
func (r *Reader) ActivateFields(names ...string) {
	r.setFieldActive(true, names)
}

func (r *Reader) setFieldActive(active bool, names []string) {
	for i, field := range r.Fields {
		for _, name := range names {
			if name == field.Name {
				prev := r.Fields[i].active
				if active && !prev {
					r.activeFields++
				} else if !active && prev {
					r.activeFields--
				}
				r.Fields[i].active = active
			}
		}
	}
}

func (r *Reader) readSep() error {
	buf := make([]byte, 1)
	if _, err := r.r.Read(buf); err != nil {
		return fmt.Errorf("error reading record separator: %w", err)
	}
	switch buf[0] {
	case recordSep:
		return nil
	case null, recordEnd:
		return io.EOF
	}
	return fmt.Errorf("invalid record separator: %x", buf[0])
}
