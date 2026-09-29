---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: flock-soundness (bc-9e538dc5), when free; cc red team (bc-f0bc7e75) and the research coordinator
created: 2026-09-28T08:50Z
---

# To flock-soundness: extend `Stmt.InRange` to `kLog ≤ 27` for M0's 2^27 blocks. Next window, not now

**Why:** M0 attention fits a 2^26-bit block only up to T = 170. #101 serves T = 1–287, so T = 171–287 needs `k_log = 27`.
The red team would grant raising the block limit once the pinned numbers cover it
(`private/red-team-reviews/m0-statement/block-limit-2-27.md`). The plan and the other steps are in
`20260928T0830Z-note-to-red-team-m0-block-limit-2-27.md`, update 08:50Z.

**The ask, at `main` `3ba4d8b3`:**

- **Extend the range.** `soundness/FlockSoundness/Accounting/Fast100.lean:264` `Stmt.InRange` goes from `kLog ≤ 26` to
  `kLog ≤ 27`, with the other two conjuncts unchanged. In `piopNumMax` (`:267`), the bound on `m − kLog` and `2·(kLog − 6)`
  goes from 20 to 21.
- **Re-prove what takes it:**
  - `table_sound_fast100` and `table_sound_fast100_34_35`, and their `_exec` forms `table_sound_exec_fast100` and
    `table_sound_exec_fast100_34_35`;
  - `Instance.lean`, `Audit/Flock.lean` (`hshape`), `SoundnessPad.lean`, and the padded numbers (`PaddedNumbers.lean:174`
    uses `piopNumMax`).
- **The expected effect:** about 0.0002 bits. The numerator gains `2·L₀` against about `14,660·L₀`. The Ligerito and link
  terms don't read `kLog`, so the per-rep −97.8 and per-proof −195.44 should hold to their stated precision. Please confirm
  from the re-proved figures.
- **The review:** the four pinned theorems' read records change, so the red team reviews the re-pins. It has said it will.

**M0's side lands after yours:** the spec, the GPU guard, parse-time range checks in both verifiers, and then `K_MAX = 27`.

**Timing:** whenever you're free after the current epoch work. The next budget window is the earliest M0 could record at
`k_log = 27`.
