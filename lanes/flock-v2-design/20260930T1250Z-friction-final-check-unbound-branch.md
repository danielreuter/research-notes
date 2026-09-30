---
id: flock-v2-design/20260930T1250Z-friction-final-check-unbound-branch
lane: flock-v2-design
kind: friction
status: open
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

# A cloud lane on its environment's branch prefix fails `checkpoint final --require-pushed` until it runs `research notes bind`

The launch message said to use the environment's prefix, so this lane's branch was `cursor/host-unit-eval-c9e2`. The final
check looked for `lane/flock-v2-design` ("no local branch lane/flock-v2-design"), and `research notes push` refused for the
same reason. `research notes bind flock-v2-design --branch cursor/host-unit-eval-c9e2 --worktree /workspace --pod none`
fixed both, at the cost of one failed FINAL.

`kb/cloud-lane-setup.md` §3 says to push "your agent's own branch instead, and name it in your first checkpoint". Adding "and
run `research notes bind <lane> --branch <it> --worktree <dir> --pod none`" there would save the next lane the failed FINAL.
