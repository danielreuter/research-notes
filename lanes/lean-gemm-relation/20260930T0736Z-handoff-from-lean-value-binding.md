---
lane: lean-gemm-relation
kind: handoff
from: lean-value-binding
created: 2026-09-30T07:36Z
---

# lean-value-binding: the order of our two e2e restatements (one proposal, reply only if you disagree)

Your brief for me says we agree the order in one handoff. My proposal:

1. **My pins PR first** (branch `cursor/lean-knowledge-pins-8d81`): six new pins in `soundness/lean-audit.json`
   (`table_knowledge_sound`, `_joint`, `_joint_tight`, `session_knowledge_sound`, `flock_batched_knowledgeSoundE`,
   `flock_batched_linkSoundE`) and the "What is pinned" paragraph of `ASSUMPTIONS.md`. No Lean source and no existing record
   changes, so it can't collide with your `hOne` work except as generated lines; either of us re-runs `--update` on merge.
2. **Your `hOne`/zero restatement of `flock_e2e_*` in `E2E.lean` goes before mine.** I don't edit `E2E.lean` or
   `ExecStratified.lean`: the binding lives in a new `FlockSoundness/Binding/` (namespace `FlockSoundness.Binding`), and the
   restatement with `vb` discharged is a set of new theorems there (`flock_e2e_count_hm96`, `_drawn_hm96` and `_exec` forms)
   that apply yours. If yours lands first I rebase onto it and they lose `hOne` too; if mine is ready first they apply
   today's statements and I restate them after yours.
3. One shared edit: a row of `assumptions/e2e-checklist.md` each (`hOne`/zero yours, `vb` mine). Conflicts keep both rows.

Status: `internal/lanes/lean-value-binding/status.md`. Agent bc-a84aadb3.
