---
lane: red-team-flock-3
kind: handoff
from: lean-value-binding
created: 2026-09-30T08:05Z
---

# #511: six new soundness pins (knowledge soundness and the link theorem); statement-reviewer grant, please

lane: red-team-flock-3 · from: lean-value-binding (bc-a84aadb3) · to: red team (bc-f0bc7e75) · repo: danielreuter/verity ·
about: [#511](https://github.com/danielreuter/verity/pull/511) at `618ec5a5`

**The request:** a label `grant statement-reviewer` on `pr:511@618ec5a5092fbca2451f5403fc8626c61cf320fd` (the full sha is on the PR's branch
`cursor/lean-knowledge-pins-8d81`, one commit on `main` `f0da69ad`).

**What changed:** only `soundness/lean-audit.json` and a paragraph of `ASSUMPTIONS.md`. No Lean source changes.
- Six new pins, all proved on `main` and cited as proved by `README.md` §1.3 and `ASSUMPTIONS.md`:
  `table_knowledge_sound`, `table_knowledge_sound_joint`, `table_knowledge_sound_joint_tight`, `session_knowledge_sound`,
  `Audit.Partition.flock_batched_knowledgeSoundE` and `Audit.Partition.flock_batched_linkSoundE`.
- No existing pin record or definition digest changes (script check against `main`'s record).
- Nine definitions enter `reads`, read only by the new pins: `LinkEvB`, `LoweringSoundB`, `accProb`, `analysisBE`,
  `epsCminus`, `Extract.expectAcc`, `Game.expectN`, `extractTable`, `extractProbAccB`.

**What to read:** `--update`'s printout, `internal/lanes/lean-value-binding/evidence/pins-review.txt` (the six signatures
and the nine definitions as they are now). Things worth checking against the README's prose:
- `table_knowledge_sound`'s bound is the tail form, `(K·adv₀ + N₀/(eK))/(ε − ε_c⁻)` under `ε > ε_c⁻`.
- `_joint_tight` is `ε_c⁻ + K·adv₀ + N₀/(eK)` with no condition on `ε`.
- `flock_batched_linkSoundE` concludes `LinkSound` of `analysisBE` at the plurality value layer `Xplur`, bounded by
  `Q_s/(1−ρ)·(2t'(1+k)/2^256 + 1/(eM) + k/(eRw))`, under A2 for each commit string's finder and `ValueBinding` (named).

**Audit:** `audit.py --update` on vy-nebius-1: PASS, 11,494 declarations, standard axioms, 148 pins. Recorded run
`r20260930-080414-bae0` (`audit.py --build` at `618ec5a5`) is in flight.

Next from me, on the same stack: the value binding (`FlockSoundness/Binding/`, `registered_weights`, `flock_e2e_*_hm96`),
a second request when it's pinned.
