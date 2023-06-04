package transcriber

import (
	"testing"
)

func TestParsingSequence(t *testing.T) {
	required := []int{1, 4, 6}
	all := []int{1, 2, 3, 4, 5, 6, 7}

	sequence := rowParsingSequence(required, all)
	expected := []step{
		{
			parse:         true,
			recordsToSkip: 0,
		},
		{
			parse:         false,
			recordsToSkip: 2,
		},
		{
			parse:         true,
			recordsToSkip: 0,
		},
		{
			parse:         false,
			recordsToSkip: 1,
		},
		{
			parse:         true,
			recordsToSkip: 0,
		},
		{
			parse:         false,
			recordsToSkip: 1,
		},
	}
	for i, step := range sequence {
		if step != expected[i] {
			t.Errorf("expected: %v, got %v", expected, sequence)
		}
	}
}

func TestParsingSequenceAllSkipped(t *testing.T) {
	required := []int{}
	all := []int{1, 2, 3, 4, 5, 6, 7}

	sequence := rowParsingSequence(required, all)
	expected := []step{
		{
			parse:         false,
			recordsToSkip: 7,
		},
	}

	for i, step := range sequence {
		if step != expected[i] {
			t.Errorf("expected: %v, got %v", expected, sequence)
		}
	}
}

func TestParsingSequenceAllRequired(t *testing.T) {
	required := []int{1, 2}
	all := []int{1, 2}

	sequence := rowParsingSequence(required, all)
	expected := []step{
		{
			parse:         true,
			recordsToSkip: 0,
		},
		{
			parse:         true,
			recordsToSkip: 0,
		},
	}
	for i, step := range sequence {
		if step != expected[i] {
			t.Errorf("expected: %v, got %v", expected, sequence)
		}
	}
}
