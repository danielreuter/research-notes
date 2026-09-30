---
lane: build-v2-kv
kind: report
created: 2026-09-30T06:40Z
status: open
---

CHECKPOINT c379497f (07:31Z) [open] attempt 1 = c379497f (+ decoder/composition share the log). r20260930-071758-4e25 failed at start (my harness copy lost its first line; fixed). WAITING r20260930-072938-7ebd on vy-nebius-1 (96-127), check after 08:15Z; agent bc-57ddc507; next: digest check + labels
CHECKPOINT e3238d3c (07:19Z) [open] attempt 1 (e3238d3c: Concat.slice bisect + K/V PartLog through rule/replay/encoder/liveness/correspondence; local 2L 1024/127 digest+corr identical, derive 34.9->19.6 s, RSS 1306->770 MB). WAITING r20260930-071758-4e25 on vy-nebius-1 (CPUs 96-127), check after 08:00Z; agent bc-57ddc507; next: digest check vs owner baseline + labels
CHECKPOINT 29f691be (06:59Z) [open] profiled main on node-1 (r20260930-064741-831b): prefill quadratic in Concat.slice/replay/encode/liveness/correspondence; decode dominated by torch export; bench CPUs now 96-127; next: Concat.slice bisect + shared K/V prefix
CHECKPOINT 29f691be (06:40Z) [open] started 06:40Z: change 3 (K/V prefix sharing), line build-v2; handoff to build-optimization 20260930T0640Z-handoff-from-build-v2-kv; next: design + local derive at 2L 1024/127; branch cursor/build-v2-kv-prefix-d717
