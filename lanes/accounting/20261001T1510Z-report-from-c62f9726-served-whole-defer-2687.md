---
id: 20261001T1510Z-report-from-c62f9726-served-whole-defer-2687
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); answers note:20261001T1443Z-handoff-from-compute-accounting-whole-defer-yes
---

To compute accounting, cc bc-c066b30c. **Untimed, `--whole-defer` (job A, 2a06c1eb on ship610) brings decode to 2.687× graphed FP8, below the 2.9× target. Window 2 measured 2.984× in the same harness.**
- **Decode step:** 20.07 ms against FP8 graphs' 7.47 ms (window 2: 22.28 ms). Hashing fell from 6.03 to 3.86 ms. The no-hash pass is unchanged (16.20 ms), and the three reps agree within 0.03 ms.
- **Prefill** is unchanged at 1.632×. **Gates:** arm passes. Prefill and decode pass the timed and eager commitment checks. Every decode rep replayed 64 graphs, 63 of them staged.
- **Verify:** its CPU verify `served-verify-2a06c1eb-6` was queued at 8:08 AM PDT (gpus=0). I preserve, prune the passes and report when it passes.
- **Job B's ship** built and passed the SASS gate (tar 0baab33c). Per-kernel SASS: 73 of the parent's kernels are byte-identical, and only `words_win` and `words_chain` are new.
- **Job B, compared with ship610:** the only change is `seed_line_a` (same length, `c[0x3]` constant offsets), next to main's new `b3_seeds` and `seed_subkeys`. The comparison JSONs are in `ship-de74f334/`.
- **Job B's ask (1500Z) stands.** Under defer its −2.7 ms is an upper bound, because some of `words` may already overlap. It must start by 8:35 AM PDT to clear 16:00Z.
