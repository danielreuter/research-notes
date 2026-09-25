---
lane: cell-verifier
kind: report
created: 2026-09-25T16:32Z
status: final
---

CHECKPOINT 7585828d (19:30Z) [final] round 3 gave up: sweep/READY absent after 40 min (18:48-19:29Z); pod 4vmp4qarp4dko7 (US-MD-1, cpu3c 32vCPU) terminated ~19:27Z by idle guard; build r20260925-184518-8bf6 only, no verifier run; endpoint3 marked STALE; round 3 ~$0.70, lane total ~$1.46
CHECKPOINT 7585828d (18:57Z) [open] round 3 build r20260925-184518-8bf6 done (flock-link 874cac3f); waiting for sweep/READY
CHECKPOINT 7585828d (18:45Z) [open] round 3 pod 4vmp4qarp4dko7 cpu3c 32vCPU US-MD-1 (GraphQL-verified, same DC as yeerzt741imi2s); endpoint3 154.54.102.15:12671 (ssh :12670); building r20260925-184518-8bf6
CHECKPOINT 7585828d (18:42Z) [open] reopened: round 3, same-DC (US-MD-1) verifier for agkr-flock-cell's batch sweep
CHECKPOINT a83d7de7 (18:15Z) [final] run1 r20260925-164419-448b (3 accepted + 1 probe); run2 r20260925-172927-6883 (5/5 accepted, 1058 rounds; producer sent 5 so server stopped by SIGTERM 18:14Z instead of 6th); both preserved rc=0; pods uv4jqaw47zdr59 (17:10Z) and ffjgm1r55fc2f7 (18:15Z) terminated; total ~$0.76
CHECKPOINT a83d7de7 (17:30Z) [open] SERVING round 2: endpoint2 157.157.221.30:26732 verifier run r20260925-172927-6883 (6 sessions, same inputs); pod ffjgm1r55fc2f7 cpu5c 16vCPU; build r20260925-172618-2bfe flock-link 83008ec3
CHECKPOINT a83d7de7 (17:17Z) [open] reopened: second verifier run (6 sessions) for agkr-flock-cell
CHECKPOINT ac57a688 (17:11Z) [final] verifier run r20260925-164419-448b (4 sessions: l0001-l0003 accepted, 1058 rounds; l0000 connected but sent no hello, no verdict; preserved rc=0), build r20260925-164033-0afb, pod uv4jqaw47zdr59 terminated 17:10Z, ~$0.28
CHECKPOINT 828ee00c (16:44Z) [open] SERVING: endpoint 154.54.102.15:19237 verifier run r20260925-164419-448b (4 sessions; prime_commitment 950d40bc..., vus 4096); build run r20260925-164033-0afb flock-link a36a7c07
CHECKPOINT 9fc78a37 (16:37Z) [open] pod uv4jqaw47zdr59 (cpu3c 16vCPU, 80GB disk; 3c/5c stock was exhausted until retry) 154.54.102.15, 7200->19237; building flock-link
CHECKPOINT 9fc78a37 (16:32Z) [open] started: non-producer verifier for agkr-flock-cell's route (a) cell; creating CPU pod vy-cell-verifier
