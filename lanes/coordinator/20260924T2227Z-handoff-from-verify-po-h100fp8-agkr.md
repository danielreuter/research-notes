---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:27Z
---

# verified: H100 FP8 A-GKR art:2e7baba7 (new Table 2 cell; verdict art:ccafc0f7)

This is lane agkr-fp8's result (891572a0, fp8-hopper, 0.688 s median), now `verified=accepted --by verify-po` with
`same_device=false`. Verdict art:ccafc0f7 is PRESERVED.
- Method as for the 4090 cell art:1b4fd4a1: main's `verity-gkr-verify` built and tested on my pod, and all 3 proofs accepted
  with the expected counts.
- The statement files are byte-identical to the producer's source (`--model hopper_e4m3_wgmma_k32`). public.bin equals
  main's frozen fp8-hopper packed y, with 0 mismatches.
- Negatives, all rejected: `mutate --sample 64` (356/356), my own claim edit, and the producer's 4 claim negatives. The
  same caveat applies: the E4M3 circuit code (07a8edd6) is not on main yet.
