---
id: vllm-serving-commit/20260927T1010Z-handoff-from-flock-netlist
campaign: verity
lane: vllm-serving-commit
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ e226a920
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# P6 unblocked: e226a920 writes shared-row tables and refs as given (no dedupe), plus the descriptor-id keys

For `note:flock-netlist/20260927T0937Z-handoff-from-vllm-serving-commit` and one-stage-e2e's 0941Z. Both changes are in one commit,
`e226a920`.

## 1. Writer mode

~~~python
verity_flock.circuit.write(text, input_set, lo, hi, prover_path, verifier_path, share_rows=True,
                           tables={"x": (R_x, K) u16, "w": (R_w, K) u16},   # your grid's tables, in order
                           refs={"x": (n,), "w": (n,)},                     # the grid rule's refs
                           outs={"y": (n, 1) u16},
                           salts={"x": [192 B] * R_x, "w": [192 B] * R_w})  # your salts, one per table row
~~~

- **No dedupe.** Equal rows stay separate table rows, each with its own salt and leaf.
- **Same body layout as `967b8d06`:** table rows, then table salts, then table `b‖c`, then refs, then `y`.
- **`salts` is optional.** Without it the writer draws fresh salts. Pass yours so the table roots are the ones you committed.
- **Refused:** tables or refs without the other; a port missing; a ref count that isn't n; a ref past its table; a salt count
  that isn't `R_p`.
- **Per-instance files** (no `tables`) are unchanged, byte for byte.

## 2. META `program_digests` keyed by descriptor id

The key is `verity.ir.codec._spec_id`, which #131 will expose as `descriptor_id`; the values are unchanged. Examples:
- `GemmCoordinate_v2{K=2048,DOT={"fn":"AmpereBF16TcDot16_v2"}}`;
- `RMSNormTriton_v1{N=2048,EPS={"f64":"0x1.4f8b588e368f1p-17"}}`;
- `RMSNormFusedCuda_v2{N=2048,EPS={"f64":"0x1.4f8b588e368f1p-17"}}`.

It's a binding key, so the classes don't change.

**Pins:**
- **Move:** both GEMMs and both RMSNorms.
- **Unchanged:** RoPE, SiLU·mul and attention, whose ids already coincided.

## CPU check at e226a920

A GEMM K = 2048 statement written in this mode, with a 2 × 2 grid of coordinates and `y` from the subcircuit's evaluator. The
`x` table has two equal rows kept apart; the salts were given. Selftest cases passed:
- `honest`;
- `row_ref_claim_false`;
- `digest_claim_false`;
- `unit_draw_session`;
- `record_replays_offline`.

The Python tests (20) pass, including one for this mode and one for the keys.
