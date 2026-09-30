---
id: 20260930T2002Z-handoff-from-proofs-state-request
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (new proofs coordinator bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4, Slack @proofs, notes lane `proofs`)
---

# @old-circuits-and-proofs: please hand @proofs your full state (workers, PRs, trains, promises, plans) in `lanes/proofs/`

I'm the new proofs coordinator (bc-8416bc72, Slack **@proofs**, notes lane **`proofs`**), under the top-level (verity-top).
You're now **@old-circuits-and-proofs**, advising (`note:20260930T1955Z-handoff-from-infra-slack-advisor-proofs`). Per
Daniel, you **keep running the merge trains** (`research merge`) until the Job queue has run one full train; then infra takes
the machinery. Everything else in the proof charter (`note:20260930T1900Z-handoff-from-verity-root-charter-proof`) is mine.

Please write one handoff to `lanes/proofs/<stamp>-handoff-from-coordinator-state.md` with:

1. **Workers:** each id you still run (the 15 in the charter plus any since), its lane, what it's doing right now, its open
   PRs and heads, and whether it's running, waiting on a pod or idle. Mark any you'd stop or merge into another.
2. **Open PRs in the proof remit:** head, grants (red team, statement reviewer), what blocks it, and its train position.
3. **Trains:** the current stack (TCP #250 with the Lean agreement build and anything after it), the queue after that, and
   which merge requests in `lanes/coordinator/` are still unanswered and whose.
4. **Promises owed:** anything you told a lane, Daniel or root you'd do, with its deadline.
5. **Plans and the Daniel items:** the GEMM-hash levers (target ~6.8×10⁶× native), unmasked-protocol completeness, the
   circuit-privacy milestone, the four Lean-organization items (including the rename-proof hash), closing #367/#372/#380/#391.
   `docs/gemm-hash-cost-plan.md`, `lean-organization.md`, `zk-proof-*.md`, `consolidation-status.md` and `merge-log.md` sit
   in verity-root's store, which my VM can't read: please paste their current decision points, or copy them to the Project
   store under `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/from-coordinator/`.
6. **Pods and spend:** every pod your workers hold, its guard and budget line.

From now on:
- **Relay:** your workers finish their current tasks and report to you; forward each result that changes a plan to
  `lanes/proofs/` (or Slack `@proofs` once your posting relay is live). New work in the proof remit goes to my workers, not
  yours.
- **Merge requests** in the proof remit still come to you for trains; I'll send mine to `lanes/coordinator/` as usual.
- **Feedback:** I'll ask you roughly daily, or before a big decision, what you'd do differently.

No deadline beyond "before your next train launch" for items 1–3; the rest when you can.
