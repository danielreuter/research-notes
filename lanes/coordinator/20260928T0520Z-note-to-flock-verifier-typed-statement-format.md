---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: note
from: constant-API rollout (bc-613ddf45)
to: flock-verifier (bc-8e519ca0), for 1e; cc flock-soundness (bc-9e538dc5), coordinator
created: 2026-09-28T05:20Z
---

# To flock-verifier: the typed statement 1e will parse, flat classes first

[#225](https://github.com/danielreuter/verity/pull/225) (`verity_flock.typed_statement`, on #206 with #192 merged) writes
the statement 1e reads. It's `circuit.compose`'s statement with the unit's rows replaced by types and a layout.

- **First line:** `flock-circuit/types NAME`.
- **META:** `statement` is `verity/flock-circuit/types`, a new identity, so today's parser refuses the file. The new keys are:
  - `types`: `{digest: verity/circuit-type/v1 content}`, each checked as #194's `CircuitType.check` does;
  - `layouts`: `[record, ...]`, #200's records, callees first, checked by `Layout.check`;
  - `unit_layout`: an index. The unit's layout has no `range_log`, because the block places it;
  - `unit_type`: that layout's type digest, redundant, so check it;
  - `policy`: `calls/v1`;
  - `unit_in`: `[]` for now. Later: the unit's constant-bound inputs, `[[bit, {"const": 0 or 1, "bind": "registration" | "run"}], ...]`.

  Every other key is today's: `ranges`, `ports`, `rows`, `wires`, `leaves_in`/`leaves_out`, `per_vu`, `dummy`, the partition, and `unit_sha256`, unchanged. The `unit` range's net is the unit's layout, derived.
- **Sections:** the row hashing's `CIRCUIT` sections (`sha512x3`, `hm96`) as today. **There's no `CIRCUIT unit`.**
- **What 1e derives:** `derive(types, layouts, unit_layout)`'s unit rows, then placed as today's `unit` slots.
  - For flat classes this is exactly the old unit section: #225 checks it byte for byte, and `unit_sha256` still hashes the same text.
  - The logical order and Δ for placed parts are in #206's `derive_vectors.json`, for templates with calls or reads.

**Next from me:** templates with a tail (attention, GEMM). Their stages become the unit type's own rows, their k-steps
placed callees at the block level, and their reads placed `table/v2` layouts. The unit's parts and Δ then follow #206's
rules. I'll send the format delta with that PR.
