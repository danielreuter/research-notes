---
id: 20261001T0137Z-handoff-from-proofs-flock-fp-vllm-jobs-on-prover-slices
campaign: verity
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-flock-fp
---

# Unpinned vLLM pipeline jobs take 5 to 9 cores of the prover slices on node 1; slice locks can't keep them off

**What:** node 1's dispatcher runs every job under `taskset -c 96-159`. The vLLM pipeline jobs pin no further:
`verity_vllm.pipeline.cli build` / `commit` / `commit-replay` / `gate`, about 20 processes at ~100% CPU each, at
6:35 PM PDT. So they run on whichever of 96-159 the scheduler picks, including 128-159. The prover lanes' slice locks
(`cpu-slices.sh`) coordinate only the jobs that take them.

**Evidence:** `cpu_slice_others` is the mean busy cores on a point's own 16-core slice that aren't its own processes:
- proofs-flock-fp: e4m3 K=16384 8.7 (r20261001-004818-8ee9), mxf4 K=2048 6.5 (r20261001-010420-9322), nvf4 K=8192 5.1
  (r20261001-012451-3788), nvf4 K=4096 3.6.
- proofs-bf16-hill: up to 3.1.
- A `ps` sample showed python processes, all `verity_vllm.pipeline.cli`, on cores 128-159 at 40-130% each.

**Why it matters:** the timed session is about 90% the CPU verifier (e4m3 K=16384: verify 13.0 s, prove 0.72 s per
statement). So session overhead moves with these jobs; prove-only overhead barely does. The points carry
`cpu-slice-shared`, so nothing is mislabelled. But the FP8/FP4 K curves mix clean and contended points.

**Recommendation (an infra decision, so not mine):** keep non-prover templates off the prover slices. One way is a
per-template cpuset in `dispatch.py`, e.g. `config-run` and `commit-pack` under 96-127 or below, provers under 128-159.
Another is a slice lock for any job that pins nothing. Until then, I'll re-run any point whose `cpu_slice_others` is
above 2 once the vLLM batch is quieter, and keep both points on the console.
