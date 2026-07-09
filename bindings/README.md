# Mnestra bindings — one interface, every language

Mnestra is **language-agnostic by construction**: the contract lives in
[`spec/mnestra.idl`](../spec/mnestra.idl) and the wire format in
[`spec/mnestra-container-format.md`](../spec/mnestra-container-format.md). Anything that can
compute BLAKE2b and speak the C ABI in [`c/mnestra.h`](c/mnestra.h) is a first-class citizen.

| Language   | File | Status |
|------------|------|--------|
| Python     | [`../mnestra/`](../mnestra) | reference implementation (runs) |
| C (ABI)    | [`c/mnestra.h`](c/mnestra.h) | header — the FFI bridge for all others |
| Rust       | [`rust/lib.rs`](rust/lib.rs) | trait surface |
| Go         | [`go/mnestra.go`](go/mnestra.go) | interface surface |
| TypeScript | [`typescript/mnestra.ts`](typescript/mnestra.ts) | interface surface |

The Python package is the executable reference; the others define the identical surface so a
team in any stack can target the same memory model and the same on-disk/on-device bytes. A
new language binding is "implement five methods + the address rule" — nothing substrate-specific
leaks across the boundary.
