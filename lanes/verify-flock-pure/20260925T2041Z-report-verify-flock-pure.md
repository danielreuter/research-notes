---
lane: verify-flock-pure
kind: report
created: 2026-09-25T20:41Z
status: open
---

CHECKPOINT a37c90d2 (23:05Z) [open] WAITING for flock-backend's fp8-hopper (H100) / bf16-ampere (A100) cell ids in lanes/verify-flock-pure/; no pod running; agent bc-fedbe934-96ea-5edf-a736-be24e2a83811; next: fetch verifier records, replay with 31-replay.sh on a fresh CPU pod, label
CHECKPOINT a37c90d2 (23:04Z) [open] reopened for more Flock cells (fp8-hopper H100, bf16-ampere A100, ...): NOT final; waiting for ids in lanes/verify-flock-pure/; budget $8 total (~$1.9 spent)
CHECKPOINT a37c90d2 (22:45Z) [final] FINAL: H100 art:6d1295ed + 4090 art:d1961ba4 verified=accepted (file re-verification, 108/108 + 102/102, r20260925-222222-a2cf); pod terminated 22:45Z ~$1.9; tip a37c90d2
CHECKPOINT a37c90d2 (22:45Z) [final] H100 art:6d1295ed + 4090 art:d1961ba4 verified=accepted (file re-verification, 108/108 + 102/102, r20260925-222222-a2cf); pod terminated 22:45Z ~$1.9; tip a37c90d2
CHECKPOINT a37c90d2 (22:36Z) [open] H100 art:6d1295ed labelled verified=accepted (108/108 sessions of verifier r20260925-220103-b7c0 replayed, negatives as expected; run r20260925-222222-a2cf). 4090 art:d1961ba4 replay running on same run; then handoff + terminate pod
CHECKPOINT d53ed556 (21:30Z) [open] old H100 cell art:bf05be17 labelled verified=accepted (60/60 sessions replayed, file re-verification). WAITING r20260925-212804-f117 on vy-verify-flock-pure (fcce H100 108 sessions + 4090 fp8-ada), check after 22:05Z; agent bc-fedbe934-96ea-5edf-a736-be24e2a83811; next: label art:1ad208b6 (+art:949bcc35), handoff, terminate pod
CHECKPOINT dc098b7b (20:56Z) [open] WAITING r20260925-205231-0e4c on vy-verify-flock-pure, check after 21:20Z; agent bc-fedbe934-96ea-5edf-a736-be24e2a83811; next: label cell r20260925-203522-4cf9 + verifier r20260925-203510-307a. So far: own instances = verifier pod's (10/10 sha256), 17/17 sessions replay-accepted; replay tool lane/verify-flock-pure dc098b7b
CHECKPOINT 7da00370 (20:41Z) [open] started 20:45Z: non-producer verifier for flock-backend H100 flock-pure-block/v2 cell; reading handoffs, locating verifier sessions; agent bc-fedbe934-96ea-5edf-a736-be24e2a83811

## FINAL

~~~text
tip: lane/verify-flock-pure @ a37c90d2 (base cursor/flock-backend-4983@a6a6e548)        merge-with: cursor/flock-backend-4983@a6a6e548
known-failures: none    pod: terminated 22:45Z; ~$1.9
artifacts: art:6d1295ed art:d1961ba4 art:bf05be17 (labelled targets); runs r20260925-222222-a2cf r20260925-220512-83dd r20260925-205231-0e4c
~~~

H100 art:6d1295ed and 4090 art:d1961ba4 verified=accepted (file re-verification: 108/108 and 102/102 sessions replayed with
own instance files, pinned lowering, own Σ/publics/link_sha256; 12/12 negatives as expected). Superseded art:bf05be17 accepted
(60/60). Handoffs received: 20260925T2100Z-handoff-from-coordinator.md, 20260925T2123Z-handoff-from-flock-backend.md,
20260925T2135Z-handoff-from-coordinator.md, 20260925T2150Z-handoff-from-coordinator.md, 20260925T2218Z-handoff-from-flock-backend.md
(all acted on). Sent: coordinator 20260925T2210Z and 20260925T2246Z.
