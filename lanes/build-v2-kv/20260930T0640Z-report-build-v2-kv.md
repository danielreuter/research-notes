---
lane: build-v2-kv
kind: report
created: 2026-09-30T06:40Z
status: open
---

CHECKPOINT 29f691be (06:59Z) [open] profiled main on node-1 (r20260930-064741-831b): prefill quadratic in Concat.slice/replay/encode/liveness/correspondence; decode dominated by torch export; bench CPUs now 96-127; next: Concat.slice bisect + shared K/V prefix
CHECKPOINT 29f691be (06:40Z) [open] started 06:40Z: change 3 (K/V prefix sharing), line build-v2; handoff to build-optimization 20260930T0640Z-handoff-from-build-v2-kv; next: design + local derive at 2L 1024/127; branch cursor/build-v2-kv-prefix-d717
