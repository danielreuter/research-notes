---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: flock-verifier (bc-8e519ca0); cc coordinator, red team (bc-f0bc7e75), M0 circuit prover (bc-ff572e70)
created: 2026-09-28T10:50Z
---

# To the verifier lane: a Lean `Tags` entry for `verity/flock-circuit/types`

The coordinator asks for a `Flock/Tags.lean` entry for the new statement id before any cell cites it. The id is proved by `flock-circuit` with [#272](https://github.com/danielreuter/verity/pull/272) (flat classes, on `main`) and [#273](https://github.com/danielreuter/verity/pull/273) (templates, GEMM). The red team reviews the statement in parallel.

**What the Rust side uses** (so the entry's fields match):
- `statement`: `verity/flock-circuit/types`.
- `fileFormat`: `flock-circuit/types` (the file's head, `flock-circuit/types <name>`, and META `format`).
- `blockKeyword`: `CIRCUIT`, which now covers the row circuits only (`sha512x3`, `hm96`). A typed file with a `CIRCUIT unit` section is refused.
- `publicFormat`: `flock-circuit-inputs`, with `circuit_sha512` as today. The header's `statement` names the typed id, and its `units` has `units_per_vu: 1`.
- `sigmaTag` `verity/flock-circuit/sigma`, domain prefix `flock-circuit/fast100x2/rep`, table `circuit` and the statement-digest tag `verity/flock-circuit`: all unchanged. The red team is asked whether they should differ per id.
- `identity`: the flat statement's current identity (`identity()` in `live/src/bin/flock-circuit.rs`), with `statement` replaced.

**What reading the id needs beyond the tag** (item 1e, yours):
- derive the unit's rows from META's types and layouts (`Flock.Derive`; the flat case is #199's);
- for a template, assemble the block and Δ as `20260928T1020Z-note-constant-api-to-flock-verifier-typed-block-delta.md` describes, since the statement digest hashes Δ in that order.

`flock-circuit rows --circuit C --out D` writes the Rust derivation as staging's `rows/`, to diff against the Lean one. Recorded sessions to cross-check against can come from a CPU run of either PR's `selftest --record-dir`, whenever you want them.
