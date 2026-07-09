# 5. Portable spec & language bindings

Mnestra is defined by a contract, not an implementation, so **every programming language is a
first-class target.**

- **Interface:** [`spec/mnestra.idl`](../spec/mnestra.idl) — five operations, neutral types.
- **Wire format:** [`spec/mnestra-container-format.md`](../spec/mnestra-container-format.md) — a trivial
  framed JSON body plus the canonical-encoding rule that fixes content addresses.
- **C ABI:** [`bindings/c/mnestra.h`](../bindings/c/mnestra.h) — the FFI bridge every other runtime
  (Rust, Go, Python/cffi, Java/JNI, Node/N-API, Swift, ...) binds against.
- **Surfaces:** Rust, Go, TypeScript stubs mirror the interface exactly; Python is the runnable
  reference.

The interoperability rule is one sentence: *the content address is BLAKE2b-128 of UTF-8 canonical
JSON (sorted keys, no insignificant whitespace).* Honour that and a pattern written by the Go
binding resolves to the identical address from Python or Rust — across substrates.

Adding a language = implement the five methods over the C ABI (or natively) and the address rule.
Nothing substrate-specific crosses the boundary, so a binding never needs to know whether it is
talking to RAM, a crystal, or a comb.
