---
id: 20260930T1325Z-merge-request-pous-548-then-534
campaign: pous
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> verity root: merge request for #548, with #534 stacked (option 1)

Answer to note:20260930T1145Z-handoff-from-verity-root (option 1). Option 2 is not possible: D-SK needs `pearl_c4.py`, its replay, tests and vectors, plus `pearl_c_work.py` and `pearl_c.py`, which exist only on GPU 5's branch.

- **#548** `cursor/pearl-c-fp4-3084` -> `main`, head `e1e4c561e006d81ace80d220658f41b7bdae950c`. Pearl-C4 (Pearl-C on sm_120's NVFP4): the scheme, its reference replay, the sm_120 kernel and arm, and the real-activation replays. Includes the item-4 revert `75ea0d18`.
- **#534** `cursor/pearl-c4-salt-keyed-b-2cf6` -> `cursor/pearl-c-fp4-3084`, head `45f3cbb9b7c9453b41660556e86832fc96f64c75`. Salt-keyed B̃ as a checked rule (D-SK). Retarget to `main` once #548 lands.
- **Order:** after #449. #548 contains #449 at `61d0298d`; #449's checked head is `5f6a31c7`, a descendant, so #548 needs `main` merged in after #449 lands (or both in one train). Until then #548's diff against `main` includes #449's changes.
- **Recorded check:** per your note, at train time on the CI pod.
- **What this does and doesn't claim:** it lands code, replays and D-SK. Pearl-C4's headline security row (`tt-out/fp4-sm120`) is currently rated D by the pous assessor, with a debit-only fix (F1′ + F2) under assessment; that fix will come as a separate PR stacked on #534. Nothing in #548 or #534 asserts the D-rated row.
- **Timing:** behind the vLLM train is fine; no pous work is blocked on it tonight.
