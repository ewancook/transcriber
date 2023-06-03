package dbf

// FieldType is a byte that represents the fields in dbase databases.
type FieldType byte

const (
	// Binary is a dbase 'binary' field.
	Binary FieldType = 'B'

	// Character is a dbase 'character' field.
	Character FieldType = 'C'

	// Date is a dbase 'date' field.
	Date FieldType = 'D'

	// Numeric is a dbase 'numeric' field.
	Numeric FieldType = 'N'

	// Logical is a dbase 'logical' field.
	Logical FieldType = 'L'

	// Float is a dbase 'float' field.
	Float FieldType = 'F'
)

// Field contains the descriptors for a field in a dbase file
type Field struct {
	Name     string
	Type     FieldType
	Length   uint8
	Decimals uint8
	active   bool
}
