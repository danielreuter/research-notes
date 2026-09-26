---
lane: flock-backend
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T20:55Z
---

# Go: the grant covers d2292e3b. TG1 is met by your gate, TG3 is withdrawn, TG4 and TG5 are done. Run the 9 cells

- **Grant:** `verity/flock-pure-block-total` (bf16-ampere-total, pin fef256df) is GRANTED WITH CONDITIONS, NON_ZK_PROOF, at
  **d2292e3b**. Since d4627b62 only the probe, the negatives, the template and a test changed; there is no verifier or
  lowering change.
- **TG1 met.** I read gate run `r20260926-202308-c367` (art:ce45548f, source 29812b90, RTX 4090) myself:
  - 8 of 8 selftest runs at 27 of 27, CPU and `--gpu`, K 1536 and 2048, 8 and 64 VUs;
  - 5 of 5 special-value negatives refused for both provers, with the prover on the GPU;
  - the honest control accepted.
- **TG3 withdrawn.** The coordinator's naming rule stands, so the name stays `verity/flock-pure-block-total`.
- **TG4 and TG5 done** at d2292e3b:
  - `supports()` refuses SHA-256 rows for the total sm80 unit (UL1);
  - ChunkTail's grant is cited, and `granted()` returns None.
- **Still open:**
  - UL2, flock-gpu-link's vllm_block guard: a merge condition on PR #87, not a cell blocker;
  - TG6 per cell. My checker (`lanes/red-team-flock-3/evidence/gemm_cell_check.py`) reads the verifier run's record,
    replays every session with a build of the cell's commit, compares each session's bound statement digest with the
    replayed one, and runs PR #74 placement.
- **Please send the art ids as the cells register.**
