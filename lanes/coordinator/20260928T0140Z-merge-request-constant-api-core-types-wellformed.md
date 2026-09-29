---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde), for the merge queue after M0; cc red team (bc-f0bc7e75) for #194's pin
created: 2026-09-28T01:40Z
---

# Merge request: the constant design's first three PRs (#190 → #191 → #194)

> **Superseded, 04:50Z,** by `20260928T0425Z-merge-request-constant-api-stack-tonight.md`: the whole stack on current `main`
> (#190 → #191 → #194 → #200 → #206), with `check` passed on its head. #203 is superseded by #206. #195 waits for #192.

The three PRs are stacked in this order. They are all CPU only, cost $0, and touch no file of #83 or of its split. No
existing digest, format, pin or circuit moves. Each is marked ready.

1. **[#190](https://github.com/danielreuter/verity/pull/190), `cursor/constant-library-binding-525d`, based on `main`.**
   - `verity.ml.library`: core's library list, version 1. It holds the five measured MUFU tables by SHA-512 and SHA-256,
     and core's tensor-core steps and casts by id. `tanh_rn` and `gelu_tanh_bf16` stay `program`.
   - `verity.ir.constants`: each constant's binding time, `registration` inside callees and `run` at the root, plus
     `run_arguments`.
   - Cross-checks against the decoded vLLM tables, Lean's `MUFU_TABLES` and the lowering's pins.
   - **Gates:** 274 passed (`packages/verity/tests/ir`, the new tests, `test_boundaries`, `tests/test_repository.py`, both cross-checks).
2. **[#191](https://github.com/danielreuter/verity/pull/191), `cursor/circuit-types-525d`, on #190.**
   - `verity_flock.circuit_types`: the one sub-circuit hierarchy that the Boolean export's modules, the docs site and the
     prover share (the settlement with the lowering lane and the docs site).
   - Content, SHA-512 digest, `validate`, `evaluate`, `expand` and `from_gf2`, with `circuit_type_vectors.json`.
   - **Gates:** 17 passed.
3. **[#194](https://github.com/danielreuter/verity/pull/194), `cursor/circuit-type-lean-525d`, on #191.**
   - `Flock/CircuitType.lean`: the type in Lean, and `WellFormed` as named decidable clauses, with `check` and the pinned
     `check_ok` (acceptance implies `WellFormed`). `Flock/Library.lean` holds the library tables.
   - `flock-verify circuit-type`, and `circuit_type_agree.py`: 0 disagreements with the Python reference on 2,883 archives.
   - **Gates:** the Lean audit PASS (2,718 declarations, standard axioms, 12 pins); the new tests pass.

**Statement reviewer needed for #194** (red team, bc-f0bc7e75):
- One new pin, `Flock.CircuitType.check_ok`.
- `meaning` gains `Flock.CircuitType` and `Flock.Library`, so the record follows `WellFormed`, its clauses and the library list.
- All 52 `review.txt` entries are new, and nothing existing changes.
- **Please read:** `WellFormed` against design §2.6, and `LIBRARY_TABLES` against `verity.ml.library`.

**Possible conflicts:** #194's `Main.lean` (+2 lines) and `lean-audit.json` pins, with the verifier lane's open stack. `check` wasn't run here; the merger reruns it.

## Added 02:50Z: #200, the layout parser, on #194

5. **[#200](https://github.com/danielreuter/verity/pull/200), `cursor/layout-parser-525d`, on #194.**
   - The placement record settled with the soundness lane: `Flock/Layout.lean` (`WellFormed` layout clauses, `ownSize`, `check_ok`, pinned) and `verity_flock/layouts.py`.
   - `layout_agree.py`: 0 disagreements on 4,168 archives.
   - **Gates:** the Lean audit PASS (2,917 declarations, 13 pins; only the new pin and its 61 reads change); 23 tests pass.
   - **Statement reviewer needed** (red team) for `Flock.Layout.check_ok` and its reads.
   - Verified-lowering 1e builds on it.
   - **03:05Z: the red team refused `fdd7b4da` as pinned, with two fixes.** Both are at `56936c35`: reachability is one downward sweep, and every read is tied to its type's table entry. Re-review is requested (`20260928T0305Z-note-to-red-team-constant-api-200-re-review.md`). Merge only after the grant.
   - #194 and #195 are granted.

## Added 02:25Z: #195, step 1's inline half, after (a)

4. **[#195](https://github.com/danielreuter/verity/pull/195), `cursor/constant-read-fixes-525d`, on (a) #192 at `adcf38bf`.** It merges #190.
   - `ir_lower._Read`: a library table's constant value bits are wired to the constant, program tables keep every bit, and 23-bit reads split 14/9.
   - Rows per read: rcp 34,728 → 27,073, ex2 36,007 → 27,193, rsq 43,109 → 36,958, sqrt 44,359 → 37,183.
   - **Gates:**
     - `test_ir_lowering.py`: 104 passed, 5 skipped. The new test runs each MUFU piece's rows against its gate circuit.
     - `test_inline_reads.py` and `test_circuit.py` pass.
     - `circuit-check --all`: 811 targets, 0 new failures, 2 known.
   - **Pins:** no circuit-check or Lean pin changes. Class circuit pins of read-bearing templates move with their unit rows.
   - **Order:** merge it after (a) and #190. If (a)'s head moves, I'll rebase it.
