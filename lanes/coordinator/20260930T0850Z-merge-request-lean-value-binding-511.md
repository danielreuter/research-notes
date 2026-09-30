---
id: 20260930T0850Z-merge-request-lean-value-binding-511
campaign: overnight-sep30
lane: lean-value-binding
kind: handoff
status: open
repo: danielreuter/verity
origin: lean-value-binding (bc-a84aadb3)
---

# Merge request (Lean train): #511 at 618ec5a5, six knowledge-soundness pins

- **PR:** [#511](https://github.com/danielreuter/verity/pull/511), branch `cursor/lean-knowledge-pins-8d81`, head
  `618ec5a5092fbca2451f5403fc8626c61cf320fd`, one commit on `main` `f0da69ad`.
- **Change:** `backends/flock/verifier/lean/soundness/lean-audit.json` (six new pins: `table_knowledge_sound`, `_joint`,
  `_joint_tight`, `session_knowledge_sound`, `Audit.Partition.flock_batched_knowledgeSoundE`, `flock_batched_linkSoundE`)
  and the "What is pinned" paragraph of `ASSUMPTIONS.md`. No Lean source changes; no existing pin or read definition changes
  (nine definitions enter `reads`).
- **Recorded audit:** `r20260930-082244-13e3` on vy-nebius-1, `audit.py --build` at the head: PASS, 11,494 declarations in
  162 modules, `propext`/`Classical.choice`/`Quot.sound`, 148 pinned theorems, kernel replay 407 s. Labels `ov.ws=security`,
  `ov.metric=pinned-theorems`, `ov.value=148`, `ov.note`.
- **Tests:** `tests/test_repository.py`, `tests/test_lean_packages.py`: 16 passed.
- **Statement reviewer:** red-team-flock-3 (bc-f0bc7e75), requested in
  `lanes/red-team-flock-3/20260930T0805Z-handoff-from-lean-value-binding-511-pins-grant.md`; **grant pending** (all six
  records are new). Don't land it before the `grant statement-reviewer` label on `pr:511@618ec5a5…`.
- **`lean-agreement`:** the change is under `backends/flock/`, but only in the nested `soundness` package, which
  `agreement_closure` leaves out. So the agreement key is `main`'s, and its pass should be reused.
- **Train notes:** only a generated record. If another Lean PR in the train changes `soundness/lean-audit.json` (lean-gemm-relation's
  `hOne` work, #490 is a different package), resolve by merging and re-running `audit.py --update`. #513 (mine) is stacked on
  it: land #511 first, or both together.
