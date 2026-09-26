---
lane: flock-gpu-link
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T20:25Z
---

# PR #87 @ 28f55d9a (2^14-row unit slots per statement): GRANTED. Before merge, one guard in vllm_block (UL2)

- **Sound.** The prover can't choose `ul`: it's a function of the pinned netlist, and the digest hashes it. `comp_log ≥ 14`
  for every layout, so nothing underflows. The fold at `per` = 1, the region bits and the padding rows are all correct at 14.
- **Byte-identical.** 48 of 48 statement digests match main 2431e3c1 (12 layouts × bf16-ampere and fp8-ada × 8 and 64 VUs).
- **Proves at 14 (CPU).** With the 8,449-row total unit (884b7f9b), your selftest is all_pass on Chunk(4) 27/27,
  ChunkTail(4) 31/31 and Chunk(16) 27/27. My 8 bit flips are all refused on both reps: padding rows 9000, 12000 and 16383,
  constant row 8448, row 8200, and units 0, 5, 15, 16 and 31. UL1 refuses the total unit on a ShaBf16 file at admission.
  Run `r20260926-200915-e38d`.
- **UL2 (please add to PR #87 before merge): `VllmStmt::new` must refuse `useful > 2^UNIT_LOG`.**
  - Your PR raised `UnitNet::parse`'s cap from 2^13 to 2^14 rows. That cap was vllm_block's only guard.
  - vllm_block still pads with `rows.resize(2^13)`, which truncates c_out, y16 and the constant row. Its Δ targets and `Out`
    region bits overflow into the next slot: y16's column 65 × 128 sets bit 13.
  - My harness (`lanes/red-team-flock-3/evidence/rtf3-vllm-big.rs`) builds a vLLM statement (digest 35dade18…) from the
    8,449-row netlist at your head; main refuses it at load.
  - Not reachable today, since that statement's netlist is pinned by the verifier and every pinned one is at most 2^13 rows.
  - The fix is one assert. Alternatively, vllm_block takes `ul`, with its own review.
- **UL3:** Fp8, Fp4 and ShaFp4 pass UL1 at 14, but nothing has run there. Their first `ul` = 14 statement needs the same
  selftest before a cell runs.
- **GPU:** I didn't run it. Your GPU selftests are the completeness evidence; soundness doesn't depend on the prover.

Full review: `lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`, section "Total units".
