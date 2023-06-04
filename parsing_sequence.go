package transcriber

type step struct {
	parse         bool
	recordsToSkip int
}

// rowParsingSequence returns a sequence of 'steps' denoting which rows are to be parsed, and which can be skipped.
// Skipped rows are aggregated so a single Skip(n) can be called, reducing the number of file seeking required.
func rowParsingSequence(required, all []int) []step {
	lookup := make(map[int]struct{})

	for _, tag := range required {
		lookup[tag] = struct{}{}
	}

	steps := make([]step, 0, 1)

	for _, tag := range all {
		if _, ok := lookup[tag]; ok {
			steps = append(steps, step{
				parse:         true,
				recordsToSkip: 0,
			})
		} else if len(steps) > 0 && !steps[len(steps)-1].parse {
			steps[len(steps)-1].recordsToSkip++
		} else {
			steps = append(steps, step{
				parse:         false,
				recordsToSkip: 1,
			})
		}
	}
	return steps
}
