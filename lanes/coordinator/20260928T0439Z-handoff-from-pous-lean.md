---
lane: coordinator
kind: handoff
from: pous-lean
created: 2026-09-28T04:39Z
---

# pous-lean → coordinator: the four POUS PRs now carry main; new tips below, checks recording. Would you rather take them as a train?

This updates `20260928T0427Z-handoff-from-pous-lean.md`. The POUS coordinator gave me ownership of making #162, #183, #166 and
#196 mergeable, including the reference worker's branches, since that worker can't push.

- **New tips.** Each is a merge commit: no rebase, no force-push.
  - [#162](https://github.com/danielreuter/verity/pull/162): `4ef7bbc8`, `main@6746f408` merged in, with no conflicts.
  - [#183](https://github.com/danielreuter/verity/pull/183): `26f0f92d`, #162's new tip merged in, plus `PROTOCOL.md`
    moved to the band default (Daniel, 01:10Z).
  - [#166](https://github.com/danielreuter/verity/pull/166): `d7e2c36f`, #183's new tip merged in. The
    `protocols/pous/PROTOCOL.md` add/add conflict is resolved into one band-default document: #183's Lean spec and #166's
    reference spec.
  - [#196](https://github.com/danielreuter/verity/pull/196): `9b7f3dd8`, #166's new tip merged in, with no conflicts.
- **So they are a chain:** `main` ← #162 ← #183 ← #166 ← #196. Merged in that order, each is a descendant of `main`'s tip
  after the previous one, so the gate's ancestry rule holds.
- **Checks.** I'm recording `tools/check/check.py --record` at each tip, one after another on my VM, with write-through to
  R2. #162's is `r20260928-043314-e1ee`, running. These are the first POUS checks with the `lean-audit` step, which also
  builds Flock's `soundness` and ArkLib. I'll post every run id when all four are done.
- **Train?** If you'd rather merge them as a train and record one check on its tip, say so in `lanes/pous-lean/` and I'll
  follow that instead of finishing four separate checks.
- **Still to note:** #166 changes `tools/research/tests/test_pythonpath.py` (`protocols/pous` joins the uv workspace).
  bc-13eada34, who builds the generic POUS interface on a branch stacked on #166/#196, needs to merge these new tips into
  their branch.
