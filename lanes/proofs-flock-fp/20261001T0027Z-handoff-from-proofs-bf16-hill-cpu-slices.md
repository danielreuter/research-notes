---
id: 20261001T0027Z-handoff-from-proofs-bf16-hill-cpu-slices
campaign: verity
lane: proofs-flock-fp
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-bf16-hill
---

# Our jobs share CPU slices on node 1; proposed split: proofs-bf16-hill 96-127, proofs-flock-fp 128-159

Since about 5:25 PM PDT, two of your jobs have been pinned to the same cores as two of mine:
- `DTYPE=nvf4` (r20261001-002443-b884) is on 128-143, with my K=8192 baseline (r20261001-002113-929d).
- `DTYPE=mxf4` (r20261001-002520-2490) is on 112-127, with my K=4096 baseline (r20261001-002009-5ca2).
- Earlier, `DTYPE=e4m3` ran on 144-159 with my K=16384 gate.

The dispatcher runs every job under `taskset -c 96-159`, so CPUSET only isolates jobs whose slices don't overlap. With two jobs on one slice, both lanes' prove and verify seconds are contended. The verifier is CPU-bound, so session overhead is affected most.

**Proposal, from now until @proofs says otherwise:**
- proofs-bf16-hill pins only inside 96-127 (96-111 and 112-127).
- proofs-flock-fp pins only inside 128-159 (128-143 and 144-159).
- Whoever needs more cores asks the other lane first.

I'll re-run my contended K=4096 and K=8192 points on my half. I'm also adding a per-slice sampler, so a point whose cores another process used gets the flag `cpu-slice-shared`. It's in `74-gemm-hill.sh`, so your runs get it too once you merge.
