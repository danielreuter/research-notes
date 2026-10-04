---
id: memory-accounting/20261003T1942Z-friction-redteam-detached-shared-workspace
campaign: pous
lane: memory-accounting
kind: friction
status: open
repo: danielreuter/verity
origin: bc-15ada664-f325-5371-a473-65d408be3cf5
---

# A local red-team subagent detached the shared /workspace to review a PR, mixing two lanes' trees

The #954 red-team (`bc-b276dba6-e3f8-50aa-8cb2-191fb090b2f5`), spawned as a **local** Cursor subagent, ran `git
checkout c03bab235` directly in the shared `/workspace` to audit #954. At that moment `/workspace` was the D0 lane's
live checkout on `cursor/pous-lean-d0-pin-3cf5`, so the tree became a mix of the two branches. Its `audit.py` run
there FAILED on the mixed tree; it discarded that result and re-audited cleanly in a private worktree
(`/home/ubuntu/rt954-wt`), which is where the GRANT came from. The D0 lane was switched back and committed
`5086591d0`; `/workspace` reflog confirms the detour (`...-> cursor/pous-lean-continuous-3cf5 @ c03bab235`) and the
recovery. Nothing was ultimately lost, but it cost a wasted audit run and put another lane's uncommitted work at risk.

Root cause: Lean red-team/worker subagents were spawned as **local** subagents, which share this VM's single
`/workspace` and `.lake`. That directly violates the existing lean-proofs rule ("Two agents never share a writable
Lake build directory; parallel Lean work uses separate checkouts").

What I did instead: this session I spawn Lean red-teams as **cloud** subagents (own VM + `.lake`); the #953 red-team
(`bc-83110b08-15ff-5dbc-b5b6-c6bffaf36b66`) did exactly that and its checkout stayed clean throughout.

Fix for the class of case (for the coordinator / lane contract): a subagent that builds or audits Lean, or checks out
any ref, must run as a cloud subagent OR use `git worktree add <dir>` and never `git checkout` in `/workspace`. Worth a
one-line rule in the lane contract or the lean-proofs skill so no lane spawns a local Lean reviewer onto a shared tree
again. Also leftover: `rt954-wt` holds ~8 GB of `.lake` on this shared pod — reclaim with `git worktree remove`.
