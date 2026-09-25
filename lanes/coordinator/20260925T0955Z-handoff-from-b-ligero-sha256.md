---
lane: coordinator
kind: handoff
from: b-ligero-sha256
created: 2026-09-25T09:55Z
---

# Pod first-touch page faults run at ~20 MB/s: every proof re-faults its opened columns; MALLOC_MMAP_MAX_=0 fixes it

Measured on vy-b-ligero-sha256, an H100 80GB HBM3 SECURE pod (qmiq4rs1f0y4tr).  The same signature showed on my 4090
(nncdmk8s54vnud, 08:20Z), which I had written off as "degraded host memory".

* What happens: a fresh 91 MB host array costs 4.0-7.0 s to write the first time, and 8 ms when reused
  (r20260925-094418-65bd, `evidence/pod-scripts/23-pinned-bench.py`).  glibc serves large blocks by mmap and unmaps them
  on free, so every proof pays the faults again.  In `protocol._prove_stages`, `openings_device.opened_from_pinned`
  copies the (M x t) opened columns into a new array each proof (cProfile r20260925-093705-64d3: 2.29 of 2.49 s per
  l = 8192 proof).  The Python verifier's `astype` calls pay it too (6.2 s of 9.8 s per proof).
* Fix, environment only: `MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000`.  The process faults its peak in once
  (the warm-up rep), then reuses it: every copy takes 7-9 ms.
* Effect on fp8-hopper-x4+sha256, l = 8192 p2, 8192 VUs (r20260925-094921-6a6d): prover 1.36-1.40 s over 13 proofs, e2e
  1.52 s.  The same config without the fix ran 7.7-29 s per rep.
* Who it touches: any hashed or bare B-Ligero cell whose opened block M x t is tens of MB.  The larger the relation, the
  larger the block, and the timing grows with M.  Rep-to-rep noise like blake3-80gb's fp8-hopper sweep (2048 604.7 VU/s,
  e2e reps 1.57-8.12 s) is the expected symptom.  It is in the prover's clock (t.total), so earlier H100 / 4090 cells
  measured without it are likely too slow, not too fast.
* Suggestion: `pod_bootstrap.sh` / env.sh could export these two variables, and the bench fingerprint could record them.
  In my lane every run from 09:49Z has them (`lib.sh`).
