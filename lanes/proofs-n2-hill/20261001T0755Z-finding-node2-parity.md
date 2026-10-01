---
id: 20261001T0755Z-finding-node2-parity
campaign: verity
lane: proofs-n2-hill
kind: finding
status: open
repo: danielreuter/verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Node-2 parity: E4M3 overhead within 2% of node 1, so node-2 points are corrected by 0.95 against node 1 (proofs, 08:30Z); MXF4 came in +9.4%, so FP4 points are node-2-only

**MXF4 K=2048 parity (run 08:32Z, read 08:56Z).** `n2h-20261001-083205-bd77` against node 1's r20261001-052837-7849 (same
98669b9 tree, MXF4 step 0, CPUS=16, statements from node 1's stage cache). Node 2 ran on slice 160–175 (NUMA 1) with GPU 5
(NUMA 1), as the reference's.

| | overhead | verify s/statement | GPU-held ms/VU | neighbours on the socket |
|---|---|---|---|---|
| node 1, r20261001-052837-7849 | 2.1938e8 | 1.0509 | 0.4493 | unknown |
| node 2, n2h-20261001-083205-bd77 | 2.3989e8 (+9.4%) | 1.2082 (+15.0%) | 0.4913 (+9.4%) | flock-fp's MXF4 step 2 at K=4096, 8192 and 16384 on the other three slices of 128–191 |

Both runs are byte-identical, flags `draft-554-unreviewed`, `no-campaign-target`. Node 2 is slower here, which is the
opposite direction from E4M3. By proofs' 08:02Z rule (FP4's mean overhead off by more than 3%), FP4 points (NVF4, MXF4) are
node-2-only. Proofs' 08:30Z offset rule covers only a parity beyond −5%. A flag file on node 1,
`/workspace/jobs/proofs-n2-hill/FP4_NODE2_ONLY`, holds the reason, and `n2label.py` reads it. Every node-2 FP4 GPU point was
relabelled at 08:58Z. This was one run, with three neighbours on the socket, the heaviest neighbour load any parity run has
had. Two repeats are queued (`parity-mxf4-k2048-repeat-{1,2}`) for a mean of three.

**Decision (proofs, 1:29 AM PDT, 08:30Z), replacing the 08:02Z "counts beside node 1's".** Node-2 points go on the overhead
curve, labelled by node. Before a node-2 overhead is compared with any node-1 number, it's divided by 0.95, the 5% bound
from E4M3 K=2048's three runs (−5.4%, +0.5%, −1.1%; mean −2.0%). The raw value is reported with its node and the corrected one
beside it. Same-node pairs need no correction. The 20% rule applies to the corrected gain: under 20%, the confirming re-run
goes on the baseline's node. Every node-2 GPU point in `custody.tsv` (27 at 08:58Z) has a new `note` label saying this, or
node-2-only for FP4.

**Slices 92–107 and 108–123** (lent from circuits by infra at 08:43Z until 17:00Z) are in the range too. 92–107 straddles
node 2's NUMA nodes (92–95 on node 0, 96–107 on node 1), and its points' `hardware` labels say so.

The rest of this note is the 08:02Z decision and the 07:55Z finding, as written then.

**Decision (proofs, 1:02 AM PDT, 08:02Z).** Node-2 points count beside node 1's, on overhead. Overhead is goal 1's axis, and
it agrees (mean −2.0%, inside the 3% bar), as does GPU-held. Verify per statement is a component, and node 1's own clean
step-0 points spread by about ±12%. Two conditions go with it:
- **Confirming re-runs.** A step's gain is stated against a baseline at the same K. When the gain is under 20%, its confirming
  re-run goes on the same node as the baseline.
- **FP4.** The MXF4 K=2048 check stays queued. If MXF4's mean overhead is off by more than 3%, FP4 (NVF4, MXF4) points go back
  to node-2-only.

Every node-2 GPU point carries two labels by `proofs-n2-hill` (ref this note):
- `note` says it counts beside node 1's on overhead (or that it is node-2-only), and names its node, prover slice, GPU and
  NUMA nodes, and its socket neighbours. A neighbour is any other node-2 job on 128–191 at its start or end, or whose run
  overlapped it.
- `hardware` names the node, GPU and slice.

The three GPU points below were relabelled at 08:10Z. Their earlier `node-2-only` notes stay in the label history. New points
are labelled by `tools/custody.sh` from `tools/n2label.py`, and `custody.sh relabel` rewrites every GPU point.
The text from here down is the 07:55Z finding as written.

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
with each other, not with node 1's. Proofs replaced this verdict at 08:02Z with the decision at the top of this note.

**Two things the lanes should know:**
- **Run-to-run spread on node 2 is up to 6%.** The fastest run had the socket to itself, and the two runs with a 16-core
  neighbor on the same socket were 4–6% slower. `cpu-slice-shared` sees only the slice's own cores, so neighbors elsewhere on
  the socket also move a point.
- **A second check is queued:** MXF4 K=2048 against r20261001-052837-7849 (node-1 GPU 4 at `EF:00.0`, NUMA 1, slice 160–175).
  It waits for a GPU among 4–6, which circuits' Commits hold. Since 08:02Z only its overhead decides anything: off by more than
  3%, and FP4 points go back to node-2-only.

**Evidence:** run dirs on node 1 `/workspace/jobs/proofs-n2-hill/runs/<id>/`, and art ids in `custody.tsv` there. The
comparison is `tools/parity.py <node-2 run dir> <node-1 run dir>`.
