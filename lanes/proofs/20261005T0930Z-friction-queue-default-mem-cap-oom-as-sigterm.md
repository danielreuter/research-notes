---
id: proofs/20261005T0930Z-friction-queue-default-mem-cap-oom-as-sigterm
campaign: flock
lane: proofs
kind: friction
status: open
repo: verity
origin: proofs
---

# A queued ad hoc job's default 8 GB memory cap kills a Lean soundness build, and the record says only SIGTERM

`research run --queue` without `--mem-gb` ran the canonical public-input worker's soundness build in a systemd scope
with `MemoryMax=8G`. One `lean` process peaked near 24 GB, so the kernel OOM-killed it, and systemd then stopped the
whole scope with SIGTERM. The run, `r20261005-064854-bd63`, was classified `UNKNOWN_SIGNAL` (rc 143) after 20 minutes,
with nothing pointing at memory. The classifier names an OOM only for a SIGKILL exit (or a `Killed` log line), not
for a scope that systemd stopped after an OOM kill inside it.

It cost 20 minutes of node 1 and a diagnosis. The rerun with `--mem-gb 96` passed (`r20261005-071424-a074`).

Better: when an OOM kill lands in a stopped scope's interval, classify the run as an OOM and print the cap it hit, or
refuse an ad hoc job with no `--mem-gb` instead of giving it a silent 8 GB.
