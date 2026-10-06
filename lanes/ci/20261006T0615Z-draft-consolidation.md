---
id: ci/20261006T0615Z-draft-consolidation
campaign: finished-state
lane: ci
kind: draft
status: open
repo: danielreuter/verity
origin: bc-81ff5c35-39a9-5232-a6b5-8e933b944292 (@ci, ci-2, for top's consolidation ask, thread 1791179949.954799)
---

# ci's consolidation: only what touches another lead's files or needs a ruling

Top asked for a short version, since tonight's implementation plan replaces the fold. Each item below is something trains hit
tonight (6 Oct, main `c305471c5` → `68e614869`) that ci can't fix inside its own code. Everything else ci does stays as it is.

| # | What broke tonight | Proposal | Whose files | Ruling? |
|---|---|---|---|---|
| 1 | #1034's red-team grant stopped carrying once main changed 3 of its `backends/flock/` files after the grant (`ba394c6b9`, then the Lean move). The PR's own change hadn't moved. `carry()` compares the change against main, so any later change on main to a granted file voids the grant. | `carry()` compares the PR's own diff (merge-base to head) at the granted head and at the new head, and carries the grant when they match byte for byte. | infra (`queue.py`); proofs (red-team policy) | Yes. It widens what a grant covers. |
| 2 | #1268 and #1258 couldn't share a train: both appended to `verity/Security/lean-audit.json`'s `meaning` list. | None for ci. Lean's merge driver (`tools/lean/merge.py`) already merges add-only records entry by entry, and `check`'s Lean audit rebuilds them on the merged tree. It refuses two different extensions of a list section such as `meaning` on purpose, which is tested. Whether to union them is lean's call. (Top approved an add-only union at 06:12Z, but it already exists.) | lean (`tools/lean/merge.py`) | No. |
| 3 | One flaky test fails a whole train check, which costs about 70 min. Tonight that was `test_placement`'s loopback connect count (7f80, fixed by #1285). Earlier it was vllm's lock probe (fixed by #1240), and flock's Merkle-collision pair failed a quick tier (#1266). | Keep fixing the tests (the owners already do). Also: `check` reruns a failed suite once on the same pod, records both results, and passes only if the rerun passes and the suite is listed as known-flaky in a file with an owner per entry. | infra, circuits and proofs (the tests); `check`'s gate | Yes. It's a change to the merge gate. |
| 4 | Checking every stacked tip at once (five tonight) took every check slot, and lane quick tiers queued for over an hour. Top had the lander cancel the middle checks. | The lander checks the top tip and the bottom tip only, and checks a middle tip only when the top fails, picking it by the failing PR's name. With #1275's trains-only slot, train checks stop taking lane slots. | old-circuits-and-proofs (lander practice); infra (#1275) | No. It's practice, agreed tonight. |

Nothing else in ci's code needs another lead or Daniel.
