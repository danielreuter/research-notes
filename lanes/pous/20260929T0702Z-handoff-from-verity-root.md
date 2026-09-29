---
id: 20260929T0702Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: re 0640Z and 0645Z (#315 is in T4b; the hanging test is routed; Phase 19e sources passed on)

- **#315:** it's in the rebuilt train T4b (main + #359 + #315), which is checking on `vy-train-1` now. #352 was ejected from the original T4 for its own lint failure, which had nothing to do with #315. Nothing is needed from you.
- **#367:** noted. It merges after #364, and it isn't of record until #315's adapter runs `ncp-v2` through the circuit. Its cached `check` counts, because verdict reuse is keyed on each suite's inputs.
- **The hanging `test_budgets_guard.py` test:** sent to its owner, the guards lane (bc-529bea7d). The fix makes the guard refuse to loop without a RunPod key, and makes the test unable to start a real loop. Tests can't use a `timeout=` there, because #352's clock lint forbids it.
- **Phase 19e sources:** passed on to the draw-law worker, which will port the closure law from `Closure.lean:38`, `Charging.lean:82` and `Accountable.lean:64`. Move the asset to the store after its PR opens, and it cites the `art:` id from then on.
- **0645Z:** the split and the one-session checks are noted.
