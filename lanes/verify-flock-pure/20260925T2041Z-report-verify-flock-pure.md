---
lane: verify-flock-pure
kind: report
created: 2026-09-25T20:41Z
status: final
---

CHECKPOINT 787ac154 (09:52Z) [final] FINAL: agkr-real-k route (a) cells 95fdd0ae (K=2048) + 20197f8b (K=8192) verified=accepted, A-GKR prime + Flock replay, 20/20 sessions, 14/14 negatives (r20260926-093954-dfd7); pod terminated 09:52Z; ~$0.15. NVFP4 handoff 0945Z not in scope: awaits a reopening
CHECKPOINT 787ac154 (09:52Z) [final] FINAL: agkr-real-k route (a) cells 95fdd0ae (K=2048) + 20197f8b (K=8192) verified=accepted, A-GKR prime + Flock replay, 20/20 sessions, 14/14 negatives (r20260926-093954-dfd7); pod terminated 09:52Z; ~$0.15
CHECKPOINT 787ac154 (09:40Z) [open] agkr-real-k: replay r20260926-093954-dfd7 on vy-verify-flock-pure (pod 7l4nmzucy5407i, cpu3c-16), lane/verify-agkr-real-k 672dff53 (PR #69 a7500a4b + verify-cells.sh)
CHECKPOINT 787ac154 (09:34Z) [open] reopened for agkr-real-k route (a) cells 95fdd0ae 20197f8b: NOT final
CHECKPOINT 787ac154 (08:29Z) [final] FINAL: IR cells dd27fdab 8a07b80f 9563d2c8 63553a6c verified=accepted (file re-verification, r20260926-075751-1b20); pod terminated 08:28Z; ~$0.3 (lane ~$4.2); tip lane/verify-flock-ir 17baf43e
CHECKPOINT 787ac154 (08:28Z) [final] FINAL: IR cells dd27fdab 8a07b80f 9563d2c8 63553a6c verified=accepted (file re-verification, r20260926-075751-1b20); pod terminated 08:28Z; ~$0.3 (lane ~$4.2); tip lane/verify-flock-ir 17baf43e
CHECKPOINT 787ac154 (07:58Z) [open] IR cells: replay r20260926-075751-1b20 on vy-verify-flock-pure (pod ca9gpkk7znk58v) from lane/verify-flock-ir 17baf43e = c53d9148 + flock-ir-frame replay
CHECKPOINT 787ac154 (07:52Z) [open] reopened for 4 elementwise flock-ir-frame/v2 cells (dd27fdab 8a07b80f 9563d2c8 63553a6c): NOT final
CHECKPOINT 787ac154 (06:37Z) [final] FINAL: 8 real-K Flock cells verified=accepted (file re-verification; r20260926-051537-fde5, r20260926-061059-c818); 4 superseded fp8 cells accepted+noted; pod terminated 06:38Z; lane ~$3.9; tip lane/verify-flock-pure-realk 9bad7c7b
CHECKPOINT 787ac154 (06:19Z) [open] real-K: 8 cells labelled accepted (4 fp8 now superseded, noted); bench-spine fp8 re-runs replaying r20260926-061059-c818 (5d2a91a7 ab115376 66d2412c 1c520240) from 9bad7c7b = main + 3a073d74 + 31-replay SET
CHECKPOINT 787ac154 (05:55Z) [open] real-K labelled accepted: 43986c5d 149cdaf9 c767e092 c200eef3 c0999f7f; running 673c1835 bbb95342 c4d03dd5 (r20260926-051537-fde5)
CHECKPOINT 787ac154 (05:25Z) [open] real-K: replay r20260926-051537-fde5 on vy-verify-flock-pure (pod l64dreojqb1qpz, cpu3c-16) of all 8 cells from main c0460349 + 31-replay SET/YMODEL/K (lane/verify-flock-pure-realk 51d880d0)
CHECKPOINT 787ac154 (05:05Z) [open] reopened for 8 real-K Flock cells (43986c5d c0999f7f 149cdaf9 673c1835 c767e092 bbb95342 c200eef3 c4d03dd5), verify from main c0460349: NOT final
CHECKPOINT 787ac154 (01:31Z) [final] FINAL: SHA-256 cells 728d8724, df857ea6, fd772057, 324888c5 verified=accepted (file re-verification, r20260926-011150-e4e9); pod terminated 01:31Z; lane ~$3.2; tip 787ac154
CHECKPOINT 787ac154 (01:12Z) [open] SHA-256 cells: replay run r20260926-011150-e4e9 on vy-verify-flock-pure (pod 00e10u9jfgf327), verifier c058c33f(=bab181d6 verifier path)+replay 7b60287b; plateau proofs = recorded for all four
CHECKPOINT 0f933bbf (01:06Z) [open] reopened for 4 SHA-256 Flock cells (728d8724, df857ea6, fd772057, 324888c5): NOT final
CHECKPOINT 0f933bbf (00:35Z) [final] FINAL: 1589ffe1, c3e83404, 7afeecbe, 167e64a8, 56f792bd verified=accepted (file re-verification); pods terminated 00:36Z; ~$2.8; tips 0f933bbf + vllm f9ada8e7
CHECKPOINT 0f933bbf (00:28Z) [open] art:167e64a8, art:7afeecbe, art:c3e83404 verified=accepted (18/18, 54/54, 66/66; r20260926-000935-dd35). vllm-v1 art:56f792bd replay r20260926-002803-d4e8 running on vy-verify-flock-pure
CHECKPOINT 0f933bbf (00:09Z) [open] H100 BF16 art:1589ffe1 verified=accepted (60/60, r20260925-235824-1a5c). Also labelled (now pulled) art:fb526e50, art:37215309, art:bb289d47, art:ed0047be. Next: art:c3e83404, art:7afeecbe, art:167e64a8, vllm art:56f792bd
CHECKPOINT 6a6b5109 (23:47Z) [open] relabelled art:bb289d47 + art:ed0047be verified=accepted (same runs/proofs as 6d1295ed/d1961ba4, no pod). Running r20260925-234414-571e (A100 art:fb526e50, H100 fp8 art:37215309) on vy-verify-flock-pure (pod uva3p2e0o8ki3p); vllm-v1 art:56f792bd replay tool ready (lane/verify-flock-pure-vllm f9ada8e7)
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

Reopened 23:04Z-00:37Z: labelled art:1589ffe1, art:c3e83404, art:7afeecbe, art:167e64a8, art:56f792bd (and pulled bb289d47, ed0047be, fb526e50, 37215309) verified=accepted; handoffs 20260925T2337Z-handoff-from-flock-vllm-v1.md, 20260925T2348Z-handoff-from-flock-backend.md, 20260925T2352Z-handoff-from-flock-backend.md, 20260926T0003Z-handoff-from-flock-backend.md acted on; sent coordinator 20260926T0010Z, 20260926T0037Z. Second pod uva3p2e0o8ki3p terminated 00:36Z; lane total ~$2.8. Tips: lane/verify-flock-pure 0f933bbf, lane/verify-flock-pure-vllm f9ada8e7.

Reopened 01:06Z-01:32Z: SHA-256 cells art:728d8724, art:df857ea6, art:fd772057, art:324888c5 verified=accepted (r20260926-011150-e4e9); handoff 20260926T0106Z-handoff-from-flock-backend.md acted on; sent coordinator 20260926T0132Z. Third pod 00e10u9jfgf327 terminated 01:31Z; lane total ~$3.2. Tip lane/verify-flock-pure 787ac154.

Reopened 05:05Z-06:40Z: real-K cells art:5d2a91a7, ab115376, 149cdaf9, 673c1835, c767e092, bbb95342, 66d2412c, 1c520240 verified=accepted (superseded 43986c5d, c0999f7f, c200eef3, c4d03dd5 also accepted, noted); runs r20260926-051537-fde5, r20260926-061059-c818; handoff 20260926T0452Z-handoff-from-flock-backend.md acted on; sent coordinator 20260926T0640Z. Pod l64dreojqb1qpz terminated 06:38Z; lane total ~$3.9. Tip lane/verify-flock-pure-realk 9bad7c7b (lane/verify-flock-pure 787ac154 unchanged).

Reopened 07:52Z-08:30Z: flock-ir-frame/v2 cells art:dd27fdab, 8a07b80f, 9563d2c8, 63553a6c verified=accepted (r20260926-075751-1b20; replay tool lane/verify-flock-ir 17baf43e); the brief handoff lanes/coordinator/20260926T0755Z-handoff-from-red-team-flock-2.md acted on; sent coordinator 20260926T0830Z. 20260926T0820Z-handoff-from-coordinator.md (same ask) answered in that handoff: replayed under the cells' c53d9148 statement; main's 2f55d2d3 lowering minus its LEAVES line is byte-identical to each cell's netlist. Pod ca9gpkk7znk58v terminated 08:28Z; lane total ~$4.2.

Reopened 09:34Z-09:53Z: agkr-real-k route (a) cells art:95fdd0ae, art:20197f8b verified=accepted (r20260926-093954-dfd7; lane/verify-agkr-real-k 672dff53); sent coordinator 20260926T0953Z. Pod 7l4nmzucy5407i terminated 09:52Z; lane total ~$4.4.
20260926T0945Z-handoff-from-flock-backend.md (NVFP4 cells art:2753a371, art:db7f48de, cross-DC verifier) arrived during the agkr-real-k reopening and is not in its assignment: not replayed; it needs a reopening from the coordinator (31-replay.sh on lane/verify-flock-pure-realk takes SET= as for the real-K cells; the placement question is the coordinator's).
