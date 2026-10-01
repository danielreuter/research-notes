---
id: 20261001T0037Z-handoff-from-proofs-take-slice-locks
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Take bf16-hill's CPU slice locks (fe8fca029) before your next node-1 run

Your runs pass no `CPUSET`, so `74-gemm-hill.sh` pins its default 96-143. That overlaps both other hillclimb lanes, and
it distorts your verifier timings most, since the verifier is CPU-bound
(`note:20261001T0036Z-handoff-from-proofs-bf16-hill-cpu-collisions`).

Take `backends/flock/pod/{74-gemm-hill.sh,cpu-slices.sh,gemm_hill.py}` from `cursor/proofs-bf16-hill-95d4` @ `fe8fca029`, with
the sampler in `1c1436102`. Your 48 cores stay, now as three locked 16-core slices. Any number you report as an overlap
win must come from a run without `cpu-slice-shared`.
