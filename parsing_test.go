package transcriber

import (
	"os"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestParseTagFile(t *testing.T) {
	tagFile, err := os.Open("tag_test.dbf")
	if err != nil {
		t.Errorf("failed to open test dbf file: %v", err)
	}

	tags, err := ParseTagFile(tagFile)
	if err != nil {
		t.Errorf("failed to parse tag file: %v", err)
	}

	expected := Tags{
		indices: []int{0, 1, 2, 3, 4, 5, 6},
		names: map[int]string{
			0: `E6\REPORTS\SPC_BLEND_600`,
			1: `E6\REPORTS\SPC_DOF_600`,
			2: `E6\REPORTS\SPC_DOF_SP_600`,
			3: `E6\REPORTS\SPC_DOF_SPH_600`,
			4: `E6\REPORTS\SPC_DOF_SPHH_600`,
			5: `E6\REPORTS\SPC_DOF_SPL_600`,
			6: `E6\REPORTS\SPC_DOF_SPLL_600`,
		},
	}
	if !cmp.Equal(expected, *tags, cmp.AllowUnexported(Tags{})) {
		t.Errorf("expected %v, got %v", expected, *tags)
	}
}
