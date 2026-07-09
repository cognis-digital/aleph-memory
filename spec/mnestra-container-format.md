# Mnestra Container Format (ACF) v0

A compact, language-neutral wire format for a `Pattern`, so any binding stores/reads the
same bytes. ACF is deliberately trivial — the value is in the *interface and addressing
discipline*, not the serialization.

## Canonical encoding (for addressing)

A content `Address` is `BLAKE2b-128(canonical(payload))` as 32 lowercase hex chars, where
`canonical` is UTF-8 JSON with keys sorted lexicographically and no insignificant whitespace.
Identical payloads → identical address on every substrate and in every language. This is the
sole rule a binding must honour to interoperate.

## Frame layout

```
+--------+---------+------------------+------------------+
| magic  | version | u32 length (LE)  | body (ACF-JSON)  |
| "ALPH" |  0x00   |                  |                  |
+--------+---------+------------------+------------------+
```

Body is the canonical JSON of:

```json
{ "text": "...", "summary": "...", "value_b64": "...", "meta": { } }
```

`value_b64` is base64 of the opaque `value` (omitted when empty).

## Substrate mapping (informative)

| Logical field | Classical (RAM/PCM) | Photonic (holography) | Quantum (AFC) |
|---|---|---|---|
| address       | hash-table key       | spectral channel id   | comb mode index |
| pattern.text  | indexed string       | hologram fringe set   | absorption-comb profile |
| query         | ANN over embeddings  | optical correlation   | quantum-associative recall |
| reconstruct   | aggregate summary    | superposed wavefront  | collective re-emission (echo) |

Bindings only ever speak the logical layer; the table is how a substrate driver realises it.
