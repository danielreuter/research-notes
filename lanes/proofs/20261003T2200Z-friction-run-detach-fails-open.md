---
id: proofs-20261003T2200Z-friction-run-detach-fails-open
campaign: soundness
lane: proofs
kind: friction
status: open
repo: verity
origin: bc-8416bc72
---
`research run --on vy-nebius-1 ... --detach` (worktree `tools/research` at /tmp/wt-q) prints "run ... launched on vy-nebius-1" and `research status` lists the run as `submitted`, but the remote tool snapshot rejects `--detach` (`research run: error: unrecognized arguments: --detach` in the run's launcher.log), so nothing runs. Four audits sat unstarted for 40 minutes (r20261003-211956-81e8, -212557-e1be, -214746-3cc3, -215635-a684) before I noticed. Fix belongs in the research tool: either forward only flags the remote snapshot accepts, or have the launcher confirm that the remote runner started (status.json present) before printing "launched". Workaround: omit `--detach`; runs already outlive the session.
