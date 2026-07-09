// Package mnestra — Go binding for the Mnestra memory interface (mirrors spec/mnestra.idl).
// A substrate driver implements Memory; callers stay substrate-agnostic.
package mnestra

type Address = string

type Pattern struct {
	Text    string
	Summary string
	Value   []byte
	Meta    map[string]string
}

type Recall struct {
	Address Address
	Score   float32
}

type GlobalView struct {
	Title       string
	Outline     []string
	Constraints []string
	Recalled    []Recall
	Filled      int
	Total       int
}

type Substrate int

const (
	Classical Substrate = iota
	Photonic
	QuantumAFC
)

// Memory is one physical substrate behind the logical model.
type Memory interface {
	Write(addr string, p Pattern) Address
	Read(addr string) (Pattern, bool)
	Query(cue string, k int) []Recall
	Reconstruct() GlobalView
}

// ContentAddress: BLAKE2b-128 of canonical-encoded payload (see ACF spec).
func ContentAddress(payload string) Address { return "" } // impl in driver

// Open returns a Memory for the chosen substrate (provided by a driver).
func Open(s Substrate) Memory { panic("provided by a substrate driver") }
