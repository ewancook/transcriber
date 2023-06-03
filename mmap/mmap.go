// Package mmap provides a wrapper around golang.org/x/exp/mmap that satisfies
// io.Reader, io.ReadSeeker, etc.
package mmap

import (
	"fmt"
	"io"

	"golang.org/x/exp/mmap"
)

// File represents a memory mapped file.
type File struct {
	reader *mmap.ReaderAt
	pos    int64
	len    int
}

// Open opens the specified file for reading. If successful, methods on
// the file can be used for reading.
func Open(filename string) (*File, error) {
	r, err := mmap.Open(filename)
	if err != nil {
		return nil, err
	}
	return &File{
		reader: r,
		pos:    0,
		len:    r.Len(),
	}, nil
}

// Read reads up to len(b) bytes from the file. It returns the number of bytes read
// and any error encountered. At the end of the file, Read returns io.EOF.
func (f *File) Read(b []byte) (n int, err error) {
	n, err = f.reader.ReadAt(b, f.pos)
	if err != nil {
		return
	}
	f.pos += int64(n)
	return
}

// Seek sets the offset for the next Read on the file to offset. This is
// interpreted according to whence: io.SeekStart seeks from the beginning
// of the file; io.SeekCurrent seeks from the current position in the file;
// io.SeekEnd seeks relative to the end of the file.Seek returns the offset
// of the file and the error, if any.
func (f *File) Seek(offset int64, whence int) (int64, error) {
	// Update pos based on input arguments
	switch whence {
	case io.SeekStart:
		f.pos = offset
	case io.SeekCurrent:
		f.pos += offset
	case io.SeekEnd:
		f.pos = int64(f.len) - offset
	default:
		return f.pos, fmt.Errorf("mmap: invalid whence")
	}
	if f.pos < 0 {
		return 0, fmt.Errorf("mmap: negative position")
	}
	return f.pos, nil
}

// Close closes the file, rendering it unsuitable for I/O. Close will return an error
// if it has already been closed.
func (f *File) Close() error {
	return f.reader.Close()
}
