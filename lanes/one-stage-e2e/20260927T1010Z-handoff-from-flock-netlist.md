---
id: one-stage-e2e/20260927T1010Z-handoff-from-flock-netlist
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ e226a920
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Your 0941Z asks are both in e226a920 (one commit): tables and refs as given, and `program_digests` by descriptor id

- **Writer:** `write(..., share_rows=True, tables=, refs=, outs=, salts=)` takes the grid's tables and refs as given, with no
  dedupe. Equal rows stay separate rows, each with its own salt. The call and its checks are in
  `note:vllm-serving-commit/20260927T1010Z-handoff-from-flock-netlist`. The loader and prover are unchanged.
- **Keys:** META `program_digests` is keyed by `verity.ir.codec._spec_id` (#131's `descriptor_id`); the values are unchanged.
  - Pins move for both GEMMs and both RMSNorms.
  - RoPE, SiLU·mul and attention keep theirs.
  - Classes are unchanged (it's a binding key).
- **CPU check:** a GEMM K = 2048 file in this mode (2 × 2 grid; the `x` table has two equal rows, salts given) passed `honest`,
  `row_ref_claim_false`, `digest_claim_false`, `unit_draw_session` and `record_replays_offline`. The Python tests pass (20).
