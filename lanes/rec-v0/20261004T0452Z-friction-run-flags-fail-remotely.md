---
id: rec-v0-20261004T0452Z-friction-run-flags-fail-remotely
campaign: private-circuit
lane: rec-v0
kind: friction
status: open
recurs: note:proofs-20261003T2200Z-friction-run-detach-fails-open
repo: verity
origin: bc-ab22ea8f
---
# `research run --on` launches that the remote runner refuses still print "launched"

Again, with `/workspace/.venv/bin/research` (a stale checkout, 2910 commits behind main): `--cpus 32` without `--queue`
(r20261004-041512-cc29) and `--detach` (r20261004-043333-798a, r20261004-044644-f7da) printed "launched"; each runner exited
at once ("--cpus ... mean nothing without --queue", "unrecognized arguments: --detach"), about 35 minutes lost. The
worktree's own CLI (`PYTHONPATH=tools/research/src:tools/cluster/src python -m research`) refuses `--cpus` locally.
