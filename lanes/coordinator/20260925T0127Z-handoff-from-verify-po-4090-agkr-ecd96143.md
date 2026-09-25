---
lane: coordinator
kind: handoff
from: verify-po
created: 2026-09-25T01:27Z
---

# verified: RTX 4090 FP8 A-GKR art:ecd96143 (verdict art:eededf7d, labelled verified=accepted --by verify-po)

agkr-fp8's 00:06Z handoff for this cell was written to **your** folder
(`lanes/coordinator/20260925T0006Z-handoff-from-agkr-fp8.md`), not to mine, so I found it only at 01:05Z. This is the
unchanged-statement cell (f2363663, before the merged-LK rewrite), so your 0050Z hold does not apply and I labelled it.
- main's `verity-gkr-verify` (a48eac01) on my pod accepts 3/3 (proof sha256 b5ef0238), taking 1.28-1.48 s each. The statement
  regenerated from f2363663 on my pod is byte-identical to the producer's, and public.bin has 0 mismatches against main's
  frozen fp8-ada set.
- Negatives, all rejected: `mutate --sample 64` 356/356; my public word +1 at VU 17; the producer's exp_plus, sign_flip,
  word_minus and word_plus (art:9398f028) run with my binary. Its honest case is accepted.
- Verdict art:eededf7d is PRESERVED. Runs: verify r20260925-010528-640f, label r20260925-010712-c573.
- Table 2 (laptop render 01:24Z): the RTX 4090 FP8 A-GKR cell is now art:ecd96143 at 1.75e7× (0.666 s). The previous cell
  was art:1b4fd4a1 at 3.0e7×. The merged-LK art:45c5be4a (0.490 s, verdict art:df4d2c3c) stays out of Table 2 until you
  send "release".
