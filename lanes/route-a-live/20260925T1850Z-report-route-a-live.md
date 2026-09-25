---
lane: route-a-live
kind: report
created: 2026-09-25T18:50Z
status: open
---

CHECKPOINT 3bc72407 (19:58Z) [open] READY verifier serving r20260925-195835-65ab on vy-route-a-live-ver 154.54.102.18:11662 (ssh :11661), US-MD-1 with the A100 154.54.102.35; sizes 1024 4096 x5. Probe r20260925-194129-7a4c: live cell OK @1024/4096 loopback (4096: 3006 prime rounds), 8192 OOM on A100 80GB (prime). Polling in turn.
CHECKPOINT 3bc72407 (19:41Z) [open] relaunched (first launch failed: --tool unregistered): probe r20260925-194129-7a4c on vy-route-a-live-a100 (setup, statements 1024-32768, loopback probe per size, negs+battery@4096), verifier setup r20260925-194138-e528 on vy-route-a-live-ver (US-MD-1 both). Staying in turn polling; READY when statements land. tip 5d1f
CHECKPOINT 3b103830 (19:20Z) [open] WAIT vy-route-a-live-a100 r20260925-191856-7028 + vy-route-a-live-ver r20260925-191913-33b3 check-back 20:00Z agent bc-9ff671e3-c69a-59c7-845e-dd0abff52276. WAITING r20260925-191856-7028 on vy-route-a-live-a100, check after 20:00Z; next: send digests to ver pod, timed same-DC run. PR #36 @ 3b103830
CHECKPOINT cba212e4 (19:12Z) [open] cba212e4 pushed (lane/route-a-live on agkr-flock-cell c95dd13a): live prime coins (Prime rounds; replay in py+rust verifiers; gates), G2 record+flock-link replay, negatives; VM tests: verifier cargo 35 ok, pytest 32 ok. Next: pod selftest + A100 cell run
CHECKPOINT b989a321 (18:50Z) [open] started: live prime coins for route (a) cell (stacked on lane/agkr-flock-cell, PR #28); agent bc-9ff671e3-c69a-59c7-845e-dd0abff52276
