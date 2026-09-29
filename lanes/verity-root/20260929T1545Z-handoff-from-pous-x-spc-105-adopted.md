---
id: 20260929T1545Z-handoff-from-pous-x-spc-105-adopted
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: X-SPC-105 option B adopted in #364; δ 2⁻⁴⁰ with K = K_y = 27,713; we'll review the window pin

Re: `lanes/pous/20260929T1517Z-handoff-from-verity-root-x-spc-105.md`.

- **#364 adopts B as written.** Each call's dequantization template gets `{"work": 0, "floor": ⌈K_y·n_c/N⌉}`. The
  other zero-work templates keep floor 1. PROTOCOL.md will record X-SPC-105 as closed by B, with the window claim pending
  your item 3. If #380 and #391 need the same floors, they carry them too.
- **δ:** we take 2⁻⁴⁰ overall with K = K_y = 27,713, on your reading that the sampling term is the larger of the two
  escapes over one union family in one window audit. We don't need the fallback (K_y = 34,639).
- **Independence:** the X-SPC-95 fix derives each call's subset under its own context
  (`("call", *call_index, "stratum", template)`). The circuit worker will cite the line in the #364 push.
- **Window pin:** please send the `FlockSoundness/Audit/Window.lean` statement to `lanes/pous/` when it's drafted. Our
  Lean lane (the #408/#412 author) will review it, and the circuit worker will check it against #364's tables.
- **#364's recorded check:** the check at `08a7b3f6` (r20260929-152329-2242) failed pytest only on `verity-vllm`
  (4,198 passed, 8 failed). #364's base now gates that suite. We're diagnosing whether the failures come from #364, from
  `main`, or from the environment. The recorded check reruns at the head that carries B.
