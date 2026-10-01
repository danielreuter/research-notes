---
id: 20261001T0037Z-handoff-from-proofs-take-slice-locks
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Take bf16-hill's CPU slice locks (fe8fca029) before your re-runs

This supersedes the "sampler only" line of `note:20261001T0034Z-handoff-from-proofs-cpu-split-and-reruns`. Take
`backends/flock/pod/{74-gemm-hill.sh,cpu-slices.sh,gemm_hill.py}` from `cursor/proofs-bf16-hill-95d4` @ `fe8fca029`, plus
`1c1436102`, and keep to 128-159. A job whose slices are held waits for them, so all three lanes' points stay clean.
Re-run e4m3, nvf4 and mxf4 at K=2048 on it.
