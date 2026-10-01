---
id: 20261001T0755Z-finding-node2-parity
campaign: verity
lane: proofs-n2-hill
kind: finding
status: open
repo: danielreuter/verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Node-2 parity: overhead agrees with node 1 (mean −2.0%), verify per statement is 4.3% faster, so node-2 points are node-2-only for now

**The point.** E4M3 GemmCoordinate{K=2048} step 0, tree `proofs-flock-fp` at 98669b9, `CPUS=16`, statements from node 1's stage
cache. The pre-stage hit both of node 1's keys (gate `c1cf413c…`, step `8b9d0f47…`), so nothing was staged on the GPU.
- **Node 1 (reference):** r20261001-052527-2ac1, slice 160–175, GPU 0 at `DB:00.0` (NUMA 0), `cpu_slice_others` 0.05.
- **Node 2:** slice 128–143 through `vy-provers` (`provers.slice`), a NUMA-0 GPU (3) as in the reference, `on=0-3`. Before
  and after each run, the slice and the range were clean: no other user-space process had affinity there.

| | overhead | verify s/statement | GPU-held ms/VU | `cpu_slice_others` | neighbor on the socket |
|---|---|---|---|---|---|
| node 1, r20261001-052527-2ac1 | 1.2688e8 | 1.3510 | 0.5197 | 0.05 | unknown |
| node 2, n2h-20261001-073720-6e5e | 1.2004e8 (−5.4%) | 1.2684 (−6.1%) | 0.4917 (−5.4%) | 0.005 | none |
| node 2, n2h-20261001-074450-4fb7 | 1.2755e8 (+0.5%) | 1.3279 (−1.7%) | 0.5225 (+0.5%) | 0.0 | proofs-arch's 16-core verifier job on 128–143 |
| node 2, n2h-20261001-074651-f94c | 1.2553e8 (−1.1%) | 1.2841 (−5.0%) | 0.5142 (−1.1%) | 0.0 | the same |
| **node-2 mean** | **−2.0%** | **−4.3%** | **−2.0%** | | |

All four runs are byte-identical, with flags `draft-554-unreviewed` only. The third run is a duplicate: the fill runner
re-ran an adopted job after its restart. That is fixed, and an attempt now never runs twice.

**Verdict, by the brief's test (all three within about 3%).** Overhead and GPU-held agree, but verify per statement doesn't.
Node 2's verifier runs about 4% faster, and every run was lower. So node-2 points are labeled `node-2-only`: they compare
with each other, not with node 1's.

**Two things the lanes should know:**
- **Run-to-run spread on node 2 is up to 6%.** The fastest run had the socket to itself, and the two runs with a 16-core
  neighbor on the same socket were 4–6% slower. `cpu-slice-shared` sees only the slice's own cores, so neighbors elsewhere on
  the socket also move a point.
- **A second check is queued:** MXF4 K=2048 against r20261001-052837-7849 (node-1 GPU 4 at `EF:00.0`, NUMA 1, slice 160–175).
  It waits for a GPU among 4–6, which circuits' Commits hold. If it lands within 3% on all three, I relabel node-2 points as
  counting beside node 1's, and say so in the lanes.

**Evidence:** run dirs on node 1 `/workspace/jobs/proofs-n2-hill/runs/<id>/`, and art ids in `custody.tsv` there. The
comparison is `tools/parity.py <node-2 run dir> <node-1 run dir>`.
