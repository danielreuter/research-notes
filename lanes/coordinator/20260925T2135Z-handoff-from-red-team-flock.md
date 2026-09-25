---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T21:35Z
---

# red-team-flock: the fp8-ada block layout of verity/flock-pure-block/v2 (PR #30 @ 48045063, RTX 4090 cell) is GRANTED WITH CONDITIONS at NON_ZK_PROOF. The bound is 2^-195.54 per 4,096-VU proof, as a union over sub-batches. Decision 57 is recorded in both earlier findings.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "fp8-ada block layout". Run
r20260925-212534-f9f0 (art:1f2fe1e9). Pod terminated at 21:31Z; about $0.10.

## Checked
- **Layout (`pure_block.rs` @ 48045063): HOLDS.**
  - One block is one VU, k_log 21. x chunk 0 (16 compressions) and chunk 1 (8), then W's; 48 units at 2^13 positions
    96–143.
  - Per-slot Δ constants:
    - the role key as the chaining input of each chunk's first compression (both chunks start from the key);
    - the counter as the chunk index, with T_HI 0;
    - block_len 64;
    - the flags KEYED_HASH, START at j = 0 and END at j = nb − 1.
  - Unit 0's c_in rows are emptied, which forces +0. The 48-unit accumulator chain and the operand-to-message copies
    stay in the block (unit u reads slot u/2, half u%2, of its role, in row byte order).
  - Public regions: the four chunk-final CVs, checked natively through keyed parents to the verifier's own row digests
    at Commit, and unit 47's c_out opened against the verifier's own `inst.out`. No intermediate value is public.
  - Dummy blocks run the same per-slot constants on zero messages.
  - The statement digest adds a layout tag for fp8. Its bf16 inputs (TAG, parameters, and Δ in the same push order)
    are unchanged, so the bf16 digest equals d3e96304's by construction, and the H100 grant carries over.
  - The instances and the netlist must name the same relation (asserted). The layout is chosen from the verifier's own
    instance file.
- **Lowering fp8-ada: HOLDS.** The netlist sha equals PINS e66262a0. It has 7,681 rows, all topological, with 65
  assertion rows (NaN operands are unsatisfiable). My differential test ran 400 random units against `verity.ml.tc`
  (ADA_E4M3), with subnormals, zeros, max-normal operands and extreme accumulators: 0 mismatches.
- **Negatives:** my rerun at 48045063 (CPU) passed fp8-ada 16/16 at 8 and 64 VUs, and the bf16 regression 18/18 at 8.
  Loopback sessions accepted; statement digests: fp8 at 8 VUs ef8f40d8…, bf16 at 8 VUs 3dae2bd2….
- **Bound:** Fast100 × 2 at m = 33 gives 2^-97.77 per rep, **2^-195.54 per 4,096-VU proof**. The region claims add
  about 2^-243. Larger batches are sub-batches, so the bound is a union over them.
- **Decision 57:** hash collision resistance is a Table 1 assumption, so no q²/2^256 term enters. The bound above is
  statistical.

## Conditions (the same as for the bf16 cell, plus two)
- **PB1:** each result names the verifier commit and binary, with the statement digest and verifier path of 48045063.
- **PB2:** the security block reports the union over sub-batches (4,096 VUs per proof on the 24 GB card).
- **PB3:** a non-producer replay labels `verified`.
- **PB4:** records carry `link_mode` exchange, `require_link` true, and the cell's Σ per sub-batch.
- **FA1:** the cell's sessions are verified by a verifier process on a separate pod serving its own instance files
  (F1). The 4090 evidence so far is loopback on the prover pod.
- **FA2 (hardening, not blocking):** add fp8 negatives for a nonzero c_in(0) and for a forged unit-47 output. The code
  enforces both (Δ empty rows; AccOut against `inst.out`), but the selftest doesn't exercise them; the bf16
  `y16_public_forged` and `committed_acc…` cases don't apply.

No fp8 bench-result exists yet, so nothing is labelled. The 4090 cell result, once built, gets `proof_class=NON_ZK_PROOF`
from me when you route it, or anyone can cite this handoff.
