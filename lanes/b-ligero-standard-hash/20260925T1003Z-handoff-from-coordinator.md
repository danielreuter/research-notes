---
lane: b-ligero-standard-hash
kind: handoff
from: coordinator
created: 2026-09-25T10:03Z
---

# Export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 in your pod runs from now (b-ligero-sha256, 0955Z)

glibc serves large blocks by mmap and unmaps them on free, so each proof re-faults its big host arrays at about 20 MB/s on
our pods: seconds per proof, and rep-to-rep noise. With the two variables set, the peak faults in once, on the warm-up rep.
On fp8-hopper-x4+sha256 at 8192 VUs, the prover went from 7.7-29 s per rep to 1.36-1.40 s. See
`lanes/coordinator/20260925T0955Z-handoff-from-b-ligero-sha256.md`.
- Set both in every measured run's environment, and say so in the checkpoint that reports the cell, until main's pod
  bootstrap sets them and the fingerprint records them (b-ligero-sha256 is making that change).
- Don't relabel or re-publish earlier numbers. A re-measured cell is a new result.
