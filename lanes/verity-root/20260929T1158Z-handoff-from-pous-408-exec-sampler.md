---
id: 20260929T1158Z-handoff-from-pous-408-exec-sampler
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (cc work-law lane bc-0b392ca4): Flock grant request for #408, the first tier-3 piece (the executable subset sampler's escape bound)

- **[#408](https://github.com/danielreuter/verity/pull/408) at `b2f8db97`** proves `Law.subset_exec_escape_le`.
  - **What it says:** `Flock.Draw.subset`'s executable sampler, over a uniform byte stream, misses `B` with probability at most `C(n−|B|, k)/C(n, k)`. That covers the rejection sampler, the `HashMap` Fisher–Yates loop and `Array.qsort`, whose membership is proved through core's `qsort.sort` and `qpartition.loop`.
  - **Axioms and audit:** standard axioms only. The audit passes with kernel replay: 61 pins, `main`'s 60 records unchanged.
  - **`Flock/Draw.lean` is not changed.**
- **Main is merged in** (`4388ac32`, including #374), so there's no `lean-audit.json` conflict in the train.
- **`meaning` gains `Flock.Draw`.** So the records of `workRule_eq_draw` and `countRule_eq_draw` now follow into the module they name. Their statements are unchanged, but the reviewers should read the grown records.
- **Please ask bc-f0bc7e75 for its grant.** POUS's statement reviewer is queued.
- **A kernel-replay gotcha for the Lean lanes:** `simp` can generate helper lemmas (`Std.Legacy.Range.mk.congr_simp`, `ByteArray.get!.eq_1`) that another module already declares, and replay rejects the duplicates. Using `rw` and `show` at those steps avoids it.
- **Status:** this is the tier-3 pilot's first mechanically connected pin. Nothing in the Python call path changes until Daniel decides the pilot.
