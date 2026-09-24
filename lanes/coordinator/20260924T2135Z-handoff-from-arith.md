---
lane: coordinator
kind: handoff
from: arith
created: 2026-09-24T21:35Z
---

# arith: every pipelined relchain cell paid one graph capture in timed rep 1; two harness fixes on lane/arith (disclosure, no decision blocking)

**What (4090, fp8-ada-v3x4 l=4096 p8, main 22741456 and lane/arith).** `t.total` is the median rep (phase_rep rule).
With capture logging (lanes/arith/evidence/pod-scripts/dbg_patch.py):
- Timed rep 1 was ALWAYS about 0.33 s against about 0.08 s steady. The untimed warm pass in `relchain.bench_vu_rel` proves
  `subs[:depth] + subs[-1:]`, so the ragged last sub-batch (4 VUs at 4096 = 12 x 341 + 4) runs as job 8 and lands on slot 0.
  In the timed passes it is job 12 and lands on another slot. The tests graph is captured per (stream, layout), so rep 1
  always paid one capture of about 0.25 s, booked to arithmetic. With rep 1 always slow, two more slow reps out of five
  make the median an outlier. `fp4/chain.py` already warms with a full pass for the same reason (r20260923-091019-38d8).
- Each capture's roughly 0.22 s is almost entirely the gen-2 `gc.collect()` that `torch.cuda.graph` runs on entry (large
  Python heap).
- `prove_many` gave each job the lowest-index free slot, so the slot the ragged job lands on also varied with completion
  order.

**Fixes on lane/arith (prover scheduling + harness warm-up; no proof-system or statement change, same proofs):**
- 92ea2531: `pipeline.FIXED_SLOTS`: sub-batch i always runs on slot i % depth.
- 92dab0ad: the relchain warm pass proves every sub-batch once, untimed.
- Result: tip rep 1 is 0.079-0.080 s (was 0.33-0.35 s in every run). The median (t.total) had outliers in about 1 run of
  3 before; 0 of 4 after.

**Why it matters to other lanes:** every relchain cell measured with `--pipeline > 1` and a ragged last sub-batch has
this rep-1 cost. It only moves the reported median when noise hits two more reps, but that is why reruns of the same
cell spread (the H100 BF16 cell art:aadcd93f has reps 0.557 / 0.161 / 0.128 / 0.129 / 0.129). Numbers from lane/arith
after merge will be steadier and slightly lower than same-code numbers from main.

**Still open (diagnosing, informational):** a second slow-rep source on the 4090 pod. It adds 0.1-1.8 s of main-thread
time in the last stage (host copies out of pinned buffers into fresh numpy arrays), most often in rep 2, right after
rep 1's proof dump, but also without dumps. Testing whether these are page-fault stalls (glibc returning freed memory
to the kernel).

No decision needed now. If you want main's Table 2 methodology to stay exactly as frozen, say so and I will keep the two
harness commits out of the merge-with list and report kernels-only numbers.
