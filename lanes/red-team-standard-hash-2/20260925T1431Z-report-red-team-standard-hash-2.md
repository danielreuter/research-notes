---
lane: red-team-standard-hash-2
kind: report
created: 2026-09-25T14:31Z
status: final
---

CHECKPOINT 041ac181 (15:10Z) [final] 15:10Z FINAL: grants bf16-hopper-x4+sha256 (1441Z) + hopper +blake3 (1453Z); proof_class on 13 cells; tile review 1455Z (no finding, 2 nits); pod terminated 14:51Z ~$0.04; branch pushed at 041ac181 (no commits)
CHECKPOINT 041ac181 (15:07Z) [final] 15:07Z FINAL: grants bf16-hopper-x4+sha256 (1441Z) + hopper +blake3 (1453Z); proof_class on 13 cells (8 hopper +blake3, 2 sha256 x4, 3 xob); tile review 1455Z (no finding, 2 nits); pod 0i9bg5qsvzcdpq terminated 14:51Z, ~$0.04; art:58d31cd3 art:c7e22b4b
CHECKPOINT 041ac181 (14:53Z) [open] 14:53Z H100 +blake3 GRANTED (16:0.5 scan 0 free/61k, control 18; H2/R1/R4 refused; art:c7e22b4b); proof_class labels on 8 hopper +blake3 cells (handoff 1453Z). tile review reply 1455Z to reverify-tile-2 (code read, 2 nits). pod 0i9bg5qsvzcdpq drained 14:51Z. Waiting on verify-night-3 for sha256/xob labels.
CHECKPOINT 041ac181 (14:46Z) [open] 14:46Z clock fix: my earlier 14:37Z/14:52Z texts ran ahead; handoff renamed 1450Z->1441Z (3 copies). H100 +blake3: H2 bf16-hopper 96 ok/48 refused, fp8-hopper 48 ok/64 refused; R4 bf16 refused; R1 fp8 refused; R1 bf16 OOM-killed, rerunning; 16:0.5 scan running.
CHECKPOINT 041ac181 (14:39Z) [open] 14:52Z bf16-hopper-x4+sha256 CLASS GRANTED WITH CONDITIONS (handoff 1450Z coordinator/verify-night-3/b-ligero-sha256; art:58d31cd3). H100 +blake3: bf16-hopper shape is 16:0.5 (not scanned) -> suite running on old pod 0i9bg5qsvzcdpq (reused, no new pod): scan 16:0.5, H2/R1/R4 both hopper.
CHECKPOINT 041ac181 (14:35Z) [open] 14:37Z item 1 evidence recovered from predecessor's pod 0i9bg5qsvzcdpq (suite finished 12:36Z at main 2c92b9e3 + overlay 041ac181): sha256 16:2 0 free rows / 150,208 mutations (control 17); H2 24 accepted 48 refused; R1 R4 refused. art:58d31cd3 PRESERVED. Grant verdict next, then labels. No new pod.
CHECKPOINT 2c92b9e3 (14:31Z) [open] 14:31Z relaunched as successor of red-team-standard-hash; branch lane/red-team-standard-hash-2 from 041ac181; reading predecessor report; queue item 1 = bf16-hopper-x4+sha256 16:2 scan

## Log

Successor of red-team-standard-hash, which died in the laptop disconnect at about 12:30Z. Branch lane/red-team-standard-hash-2
@ 041ac181, cut from lane/red-team-standard-hash per relaunch-branches-0725. No code commits.

* 14:31Z inbox: 20 handoffs inherited from red-team-standard-hash, all already acted on in its report except 1202Z (below).
* 14:33Z the predecessor's pod 0i9bg5qsvzcdpq (vy-red-team-sh, cpu3c 4 vCPU, $0.12/h) was still up. Its suite
  `xob_bf16sha_suite.sh` had finished at 12:36Z, including the bf16-hopper-x4+sha256 half, which was never reported.
  Outputs pulled and preserved as art:58d31cd3. The r4 proofs are omitted, but every file is hashed in `bf16sha.sha256`.
* 14:41Z handoff to the coordinator, cc verify-night-3 and b-ligero-sha256: "bf16-hopper-x4+sha256 @main 2c92b9e3: CLASS
  GRANTED WITH CONDITIONS" (reply to 1202Z). The 16:2 scan found 0 free rows in 150,208 mutations (control 17). H2: 24 accepted, 48 refused. R1 and R4 refused.
* 14:40Z shape check for the H100 +blake3 cells. fp8-hopper is 48×32 E4M3 words, shape 8:0.5 (scanned). bf16-hopper is
  96×16 BF16 words, shape 16:0.5 (NOT scanned). Suite `evidence/pod-scripts/hopper_blake3_suite.sh` (plus `_h2b.sh`, and an
  R1 rerun after an OOM kill at the 8 GB cgroup) ran on the same pod, at main 2c92b9e3 plus overlay 041ac181, binary 9602aba7.
  Results: 16:0.5 has 0 free rows in 61,428 mutations (control 18). H2: bf16 96 accepted, 48 refused; 128 and 192 are refused
  by the prover's 2..3-chunk rule, the known completeness nit. fp8 48 accepted, 64 refused. R1 and R4 refused on both. art:c7e22b4b.
  (art:9c5fe8a6 is a broken first upload, stdout garbage in the tgz. Do not cite it.)
* 14:51Z `research pods drain 0i9bg5qsvzcdpq`: terminated, nothing unpreserved. Up 12:13-14:51Z, about $0.32 in total; this lane's share is about $0.04.
* 14:52Z `proof_class=COMPLETE_ZK_BACKEND` and `finding` (by red-team-standard-hash, ref coordinator/1453Z) on the 8 hopper
  +blake3 cells verify-night-2 accepted at main 2c92b9e3: art:c8730574, art:7c6b4647, art:9c11326c, art:7a3965da,
  art:d33257bb, art:a36d1405, art:41f7727f, art:1ea7c359. On both replicas. Handoff to the coordinator, cc verify-night-3 and blake3-80gb.
* 14:41Z received `20260925T1445Z-handoff-from-reverify-tile-2.md` ("Review request: the +shared (v6) tile recomputation").
  Code read at 4ee9dd72, with no soundness finding. Two nits: a float seed makes reverify raise TypeError instead of a clean FAIL, and
  `set.sharing` is not cross-checked. Reply `reverify-tile-2/20260925T1455Z-handoff-from-red-team-standard-hash-2.md`.
* Clock: my first two checkpoint texts said 14:37Z and 14:52Z, ahead of real UTC; the stamps are right. The first handoff
  was renamed from 1450Z to 1441Z.
* 14:59Z and 15:03Z received `20260925T1502Z-handoff-from-verify-night-3.md` ("verified=accepted: 3 blake3-xob cells +
  bf16-hopper-x4+sha256 art:fcd6a623") and `20260925T1507Z-handoff-from-verify-night-3.md` ("verified=accepted:
  fp8-hopper-x4+sha256 art:4aa258ee"). I read the 977ad27b reverify diff: it changes only where the manifest is found.
  15:06Z labelled `proof_class=COMPLETE_ZK_BACKEND` and `finding` on art:4aa258ee (ref 1033Z), art:fcd6a623 (ref 1441Z),
  art:b47828e4, art:bb69174b and art:ecccca50 (ref 1226Z). On both replicas. 15:07Z handoff to the coordinator.

## FINAL

~~~text
tip: lane/red-team-standard-hash-2 @ 041ac181 (base lane/red-team-standard-hash@041ac181)        merge-with: none
known-failures: none    pod: terminated 14:51Z (0i9bg5qsvzcdpq, the predecessor's pod reused); about $0.04 this lane (pod total about $0.32)
artifacts: art:58d31cd3 art:c7e22b4b
~~~

Grants: bf16-hopper-x4+sha256 (1441Z) and bf16-hopper+blake3 / fp8-hopper+blake3 (1453Z), both CLASS GRANTED WITH CONDITIONS.
Labels: 13 cells have proof_class=COMPLETE_ZK_BACKEND: the 8 hopper +blake3 cells, 2 +sha256 x4 cells and 3 blake3-xob cells.
Tile review (reverify-tile-2 1455Z): code read only, no soundness finding, 2 nits. Left open: the x1 +blake3-xob plateau
(no artifact id and no verified label yet), and an end-to-end run of the tile negatives (a missing `.hproof`, a float seed).

Inherited handoffs: all 20 were addressed to red-team-standard-hash and acted on in its report (`lanes/red-team-standard-hash/20260925T0715Z-report-red-team-standard-hash.md`), except 1202Z, which is answered here at 1441Z:
- red-team-standard-hash/20260925T0745Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T0752Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T0844Z-handoff-from-blake3-80gb.md
- red-team-standard-hash/20260925T0850Z-handoff-from-verify-night-2.md
- red-team-standard-hash/20260925T0905Z-handoff-from-b-ligero-standard-hash.md
- red-team-standard-hash/20260925T0935Z-handoff-from-blake3-80gb.md
- red-team-standard-hash/20260925T0935Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T0937Z-handoff-from-ligero-steps-pin.md
- red-team-standard-hash/20260925T0946Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1000Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1017Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1045Z-handoff-from-blake3-80gb.md
- red-team-standard-hash/20260925T1055Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1105Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1131Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1146Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1150Z-handoff-from-b-ligero-standard-hash.md
- red-team-standard-hash/20260925T1152Z-handoff-from-b-ligero-sha256.md
- red-team-standard-hash/20260925T1202Z-handoff-from-coordinator.md
- red-team-standard-hash/20260925T1320Z-handoff-from-b-ligero-standard-hash.md
