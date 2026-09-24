---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-24T22:06Z
---

# verified: RTX 4090 FP8 A-GKR art:1b4fd4a1 (new Table 2 cell; verdict art:a40f5576)

This is lane agkr-fp8's result (07a8edd6, fp8-ada, 1.130 s median), now `verified=accepted --by verify-po` with
`same_device=false`. Verdict art:a40f5576 is PRESERVED.
- Verifier: `verity-gkr-verify` built and tested (8/8) on my pod from main ab9573fd. `backends/gkr/verifier` is unchanged at
  07a8edd6. All 3 proofs are accepted with the counts the producer expected.
- Statement: main has no E4M3 A-GKR builder, so I regenerated the circuit files with the producer's named source (07a8edd6)
  on my pod. They are byte-identical to the dump. public.bin equals pack_public(final FP32 word) of the frozen fp8-ada set
  drawn by main, with 0 mismatches.
- Negatives, all rejected: `mutate --sample 64` (356/356); my public word +1; the producer's 4 claim negatives, run with my
  binary.
- Caveat: the circuit's correctness as an E4M3 arithmetisation rests on 07a8edd6 code that main does not have yet. This is
  the same position as the Hopper A-GKR cell before its merge.
- The producer's own known metadata slip is left as is: the BF16 descriptive strings in `software`/`note`.
