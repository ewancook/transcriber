package transcriber

import (
	"bytes"
	"testing"
)

var rows = []Row{
	{
		date: []byte("22/08/2021"),
		time: []byte("13:11:00"),
		values: []Datum{
			{
				column: 0,
				value:  12.12312312,
			},
			{
				column: 1,
				value:  11.94029,
			},
		},
	},
	{
		date: []byte("22/08/2021"),
		time: []byte("13:12:00"),
		values: []Datum{
			{
				column: 0,
				value:  11.93356209,
			},
			{
				column: 1,
				value:  11.94029,
			},
		},
	},
	{
		date: []byte("22/08/2021"),
		time: []byte("13:13:00"),
		values: []Datum{
			{
				column: 1,
				value:  11.94029,
			},
		},
	},
}

var (
	tags = [][]byte{
		[]byte("TagName1"),
		[]byte("TagName2"),
	}
	precision     = 8
	rowsToAverage = 30
)

func TestWriteHeader(t *testing.T) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	w.WriteHeader(tags)
	result := buf.String()
	expected := "Date,Time,TagName1,TagName2\n"

	if result != expected {
		t.Errorf("got %s, expected %s", result, expected)
	}
}

func TestWriteRow(t *testing.T) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	// values should have the correct precision, whether they are truncated or padded.
	expected := []string{
		"22/08/2021,13:11:00,12.12312312,11.94029000\n",
		"22/08/2021,13:12:00,11.93356209,11.94029000\n",
		"22/08/2021,13:13:00,,11.94029000\n",
	}

	for i := range rows {
		w.WriteRow(rows[i])
		result := buf.String()
		if result != expected[i] {
			t.Errorf("got: %s, expected %s", result, expected[i])
		}
		buf.Reset()
	}
}

func TestWriteAveragedRow(t *testing.T) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	w.WriteAveragedRow(rows)
	result := buf.String()

	// values should have the correct precision, whether they are truncated or padded.
	expected := "22/08/2021,13:13:00,12.02834261,11.94029000\n"

	if result != expected {
		t.Errorf("got %s, expected %s", result, expected)
	}
}

func TestWriteBlankRow(t *testing.T) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	w.WriteRow(Row{
		date:   []byte("22/08/2021"),
		time:   []byte("13:14:00"),
		values: nil,
	})
	result := buf.String()

	// values should have the correct precision, whether they are truncated or padded.
	expected := "22/08/2021,13:14:00,,\n"

	if result != expected {
		t.Errorf("got %s, expected %s", result, expected)
	}
}

func TestWriteBlankAveragedRow(t *testing.T) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	w.WriteAveragedRow([]Row{{
		date:   []byte("22/08/2021"),
		time:   []byte("13:14:00"),
		values: nil,
	}})
	result := buf.String()

	// values should have the correct precision, whether they are truncated or padded.
	expected := "22/08/2021,13:14:00,,\n"

	if result != expected {
		t.Errorf("got %s, expected %s", result, expected)
	}
}

func BenchmarkWriteHeader(b *testing.B) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	for n := 0; n < b.N; n++ {
		w.WriteHeader(tags)
	}
}

func BenchmarkWriteRow(b *testing.B) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	for n := 0; n < b.N; n++ {
		w.WriteRow(rows[0])
	}
}

func BenchmarkWriteAveragedRow(b *testing.B) {
	buf := new(bytes.Buffer)
	w := NewWriter(buf, tags, precision)

	for n := 0; n < b.N; n++ {
		w.WriteAveragedRow(rows)
	}
}
