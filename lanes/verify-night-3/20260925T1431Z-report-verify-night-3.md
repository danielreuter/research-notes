---
lane: verify-night-3
kind: report
created: 2026-09-25T14:31Z
status: final
---

CHECKPOINT 7585828d (06:33Z) [final] 9/9 sp1-evaluator SP1 proofs verified=accepted + below_bar=true + note (run r20260926-053354-a19b @main 3d57f08b: APPROVED key reproduced, statements rebuilt equal, core+compressed verify_object, 3 negatives refused). Pod heudtct27whkty terminated 06:31Z; ~$0.9. Handoff 0635Z to coordinator
CHECKPOINT 7585828d (05:39Z) [open] BUSY (do not reap): pod vy-verify-night-3 heudtct27whkty (cpu5c 16 vCPU $0.56/h, guard 60) runs r20260926-053354-a19b: host built, APPROVED identity reproduced (ELF cef2b78a, vk 0x007d9347), verifying 9 SP1 results now (~30-45 min). Run 044301-0e46 failed my setup (libprotobuf-dev missing), not reaped. Check back ~06:20Z
CHECKPOINT 7585828d (04:43Z) [open] BUSY (do not reap): pod vy-verify-night-3 jnp5k2d0vy9z2h (cpu3c 16 vCPU $0.48/h) runs r20260926-044301-0e46 @main 3d57f08b: SP1 CPU host build (~25 min) then 9 SP1 below-bar verifications. First launch r20260926-035411-44ce was reaped mid-build at 04:06Z (pod rd921ysua7g60b gone, no result). Check back ~05:25Z
CHECKPOINT 7585828d (03:56Z) [open] WAITING: pod vy-verify-night-3 rd921ysua7g60b (cpu3c 32 vCPU, $0.96/h, guard 30); run r20260926-035411-44ce @main 3d57f08b: build CPU veritor-zk-host (APPROVED check), then per art (9 SP1 results): proof sha vs run record, prepare rebuild (object digest + statement sha), verify_object core+compressed, 3 negatives. Check ~04:25Z
CHECKPOINT 7585828d (03:50Z) [open] reopened (cloud) for SP1 below-bar verification per 0305Z handoff: NOT final
CHECKPOINT 906255b2 (23:49Z) [final] H100 blake3-xob x4: 955a52e0 (vd 120b459a) + f15909f5 (vd f8b8836c) accepted @main 6c3568dc; equiv 72745743 (c43ec491) + 04f24f73 (835ca8d9) accepted; handoffs to red-team-standard-hash-2 + coordinator. Pod o2gvkt3wwmn1le terminated 23:41Z ~$0.35
CHECKPOINT 906255b2 (23:45Z) [final] H100 blake3-xob x4: 955a52e0 (vd 120b459a) + f15909f5 (vd f8b8836c) accepted @main 6c3568dc; equiv 72745743 (c43ec491) + 04f24f73 (835ca8d9) accepted; handoffs to red-team-standard-hash-2 + coordinator. Pod o2gvkt3wwmn1le terminated 23:41Z ~$0.35
CHECKPOINT 906255b2 (23:44Z) [final] H100 blake3-xob x4: 955a52e0 (vd 120b459a) + f15909f5 (vd f8b8836c) accepted @main 6c3568dc; equiv 72745743 (c43ec491) + 04f24f73 (835ca8d9) accepted; handoffs to red-team-standard-hash-2 + coordinator. Pod o2gvkt3wwmn1le terminated 23:41Z ~$0.35
CHECKPOINT 906255b2 (23:23Z) [open] pod vy-verify-night-3 o2gvkt3wwmn1le (cpu3c 32 vCPU, $0.96/h) for H100 blake3-xob x4 955a52e0/f15909f5 + equiv 72745743/04f24f73 @main 6c3568dc (pins 775786b7)
CHECKPOINT 906255b2 (23:21Z) [open] reopened: H100 blake3-xob x4 fp8 955a52e0 / bf16 f15909f5 + equiv 72745743 / 04f24f73 (coordinator 23:21Z): NOT final
CHECKPOINT 906255b2 (22:25Z) [final] route (a) re-registration art:77411c93 verified=accepted (vd eb1a010f; same 5 proofs and records as the G3 gate, envelope-only changes); no pod
CHECKPOINT 906255b2 (22:23Z) [final] route (a) re-registration art:77411c93 verified=accepted (vd eb1a010f; same 5 proofs and records as the G3 gate, envelope-only changes); no pod
CHECKPOINT 906255b2 (22:22Z) [open] reopened: relabel route (a) art:77411c93 (route-a-live 2225Z), no pod: NOT final
CHECKPOINT 906255b2 (22:07Z) [final] route (a) art:4b52879f accepted (vd 317fe4b7; rederive reproduces), art:aa9223c2 note only (unpinned 1024); H100 +blake3 x4 d88a9948 (ea920793) + 5ea60c40 (e6b6b5c2) accepted @main 78b8935b; equiv a400cae2 (9d8a1137) + 6b27220a (d782b585) accepted. Pod i86pg3pvzc9vjm terminated 22:09Z ~$0.50
CHECKPOINT 906255b2 (22:06Z) [final] route (a) art:4b52879f accepted (vd 317fe4b7, same proofs as G3); H100 +blake3 x4 d88a9948 (ea920793) + 5ea60c40 (e6b6b5c2) accepted @main 78b8935b; equiv a400cae2 (9d8a1137) + 6b27220a (d782b585) accepted. Pod i86pg3pvzc9vjm terminated 22:09Z ~$0.50
CHECKPOINT 906255b2 (21:41Z) [open] route (a) art:4b52879f verified=accepted (vd art:317fe4b7; same 5 proofs as my G3 gate). Pod vy-verify-night-3 i86pg3pvzc9vjm (cpu3c 32 vCPU, $0.96/h) for H100 +blake3 x4 d88a9948/5ea60c40 + equiv a400cae2/6b27220a @main 78b8935b
CHECKPOINT 906255b2 (21:38Z) [open] reopened (coordinator 2140Z): relabel route (a) art:4b52879f; verify H100 +blake3 x4 art:d88a9948 / art:5ea60c40 + equiv: NOT final
CHECKPOINT 906255b2 (20:53Z) [final] route (a) G3: art:3bfb2f58 verified=accepted (gate battery + offline Flock replay re-run from the store, statements regenerated and equal; runs r20260925-203452-5265 / -204110-326f); art:d5731679 note only ([0,1024) commitment unpinned; accepts with --allow-unpinned-commitment, r20260925-204749-26c6). Pod 7qkora4f5oy6t9 terminated 20:52Z ~$0.15
CHECKPOINT dec08973 (20:41Z) [open] G3 run 1 r20260925-203452-5265: 4096 honest s1-s5 pass every check but non_producer (prime + Flock replay accept), negatives reject; 1024 prime verify rc 2 (public.bin not in store). Run 2: regenerate statements myself + battery again
CHECKPOINT 906255b2 (20:34Z) [open] pod vy-verify-night-3 7qkora4f5oy6t9 (cpu3c 16 vCPU, $0.48/h) for route (a) G3: gate battery + offline Flock replay from the store @dec08973
CHECKPOINT 906255b2 (20:28Z) [open] reopened for route (a) live-coin G3 (art:3bfb2f58 4096, envelope art:d5731679; PR #36 dec08973): NOT final
CHECKPOINT 906255b2 (20:22Z) [final] 4 cells + 4 equiv accepted: ac1f532c(833fc972)+dc455fc8(388e52d3), 675a03a3(19d49495)+40b23d0b arrays direct(16c71390), f7aac95f(83483c9f)+d4402d29(7d6d25db), H100 6d6464d1(c319dee2)+9b5f1e24(c42c70b9); pod p3ink8nhwnomt7 terminated 20:21Z ~$0.30
CHECKPOINT 906255b2 (20:21Z) [final] 4 cells + 4 equiv accepted: ac1f532c(833fc972)+dc455fc8(388e52d3), 675a03a3(19d49495)+40b23d0b arrays direct(16c71390), f7aac95f(83483c9f)+d4402d29(7d6d25db), H100 6d6464d1(c319dee2)+9b5f1e24(c42c70b9); pod p3ink8nhwnomt7 terminated 20:21Z ~$0.30
CHECKPOINT 906255b2 (20:13Z) [open] accepted: 675a03a3 (vd 19d49495), ac1f532c (833fc972), f7aac95f (83483c9f) + 3 equiv. Queue +1: H100 fp8-hopper-x4+vllm-v1 art:6d6464d1 (equiv 9b5f1e24) running @acd50fec
CHECKPOINT 906255b2 (20:00Z) [open] equiv accepted: dc455fc8 (vd 388e52d3), 40b23d0b arrays direct (vd 16c71390), d4402d29 regen at acd50fec + 7da00370 (vd 7d6d25db). reverify: 675a03a3 PASS; ac1f532c running, then f7aac95f
CHECKPOINT 906255b2 (19:48Z) [open] pod vy-verify-night-3 p3ink8nhwnomt7 (cpu3c 16 vCPU 100GB, $0.48/h) for ac1f532c/675a03a3 (@main 7da00370) + f7aac95f (@lane/b-ligero-vllm-v1 acd50fec) and their equiv docs
CHECKPOINT 906255b2 (19:42Z) [open] reopened for 3 cells (coordinator 1940Z/1945Z): ac1f532c+dc455fc8, 675a03a3+40b23d0b, f7aac95f+d4402d29: NOT final
CHECKPOINT 906255b2 (19:41Z) [final] flock-backend CPU drill-down art:827f594c verified=accepted (replay r20260925-193306-85c5, 18/18 sessions of art:904398d8); pod mzclpkcwdyp4xm terminated 19:39Z ~$0.10. Coordinator 1940Z/1945Z queue (2 sha256 cells + vllm-v1 cell) NOT taken: needs a new launch
CHECKPOINT 906255b2 (19:39Z) [final] flock-backend CPU drill-down art:827f594c verified=accepted: 20-pure.sh replay @ab5c1156 run r20260925-193306-85c5, 18/18 sessions of art:904398d8 accepted, lowering da1bbe2c PINNED; note: CPU drill-down (rule K). Pod mzclpkcwdyp4xm terminated 19:39Z, ~$0.10
CHECKPOINT 906255b2 (19:31Z) [open] pod vy-verify-night-3 mzclpkcwdyp4xm (cpu3c 16 vCPU, $0.48/h, guard 30) for flock replay; staging art:904398d8 then 20-pure.sh MODE=replay @ab5c1156
CHECKPOINT 906255b2 (19:25Z) [open] reopened for flock-backend CPU drill-down replay (art:827f594c / art:904398d8, coordinator 19:24Z): NOT final; will create one cheap CPU pod vy-verify-night-3 (budget $3)
CHECKPOINT 906255b2 (15:04Z) [final] 7/7 accepted: equiv d9b3724d->73aa7efe, b6f2e1df->7b44bcad; xob b47828e4->cc5f72de, bb69174b->99a5a9fd, ecccca50->47cf9051; sha256 fcd6a623->192c1ed9, 4aa258ee->3b2b8e2f (reverify root-layout fix 977ad27b, merge-ready 906255b2). 5090 NVFP4 still fail-closed. Pod terminated 15:06Z, ~$0.30
CHECKPOINT 977ad27b (14:59Z) [open] accepted: xob b47828e4 (vd cc5f72de), bb69174b (99a5a9fd), ecccca50 (47cf9051); sha256 fcd6a623 (192c1ed9, via reverify fix 977ad27b). Handoff red-team-standard-hash-2 1502Z. Running 4aa258ee r20260925-145803-dd7d
CHECKPOINT 977ad27b (14:51Z) [open] xob b47828e4 + bb69174b PASS (labels pending push); ecccca50 running. sha256 fcd6a623 ERROR (tree has proofs at root, no proofs/): reverify patched 977ad27b to read root layout, rerunning; 4aa258ee fetching
CHECKPOINT a5d9b632 (14:45Z) [open] equiv art:d9b3724d (x4 8192) -> verdict art:73aa7efe, art:b6f2e1df (x4 32768) -> art:7b44bcad: both --check reproduce, equal=True, candidate == result instances; verified=accepted, preserved. Renderer _equiv_content @2c92b9e3 still wants frozen==[0,4096] (coord told). Running: reverify sha256 fcd6a623/4aa258ee, xob b47828e4/bb69174b/ecccca50
CHECKPOINT a5d9b632 (14:38Z) [open] H100 +blake3 table rows (c8730574 7c6b4647 9c11326c 7a3965da) already verified=accepted by verify-night-2 -> item 3 done. Pod bootstrapping (frozen set + cargo). Queue: equiv d9b3724d/b6f2e1df, sha256 4aa258ee/fcd6a623, xob b47828e4/bb69174b/ecccca50
CHECKPOINT a5d9b632 (14:35Z) [open] pod vy-verify-night-3 k2ww8qvkhxlvab (cpu3c 16vCPU, 150GB, guard 30) bootstrapping r20260925-143459-f66c; verifier tree lane/verify-night-3 a5d9b632 = main 2c92b9e3 + 5b28557b (xob pins); next: equiv d9b3724d/b6f2e1df, sha256 x4
CHECKPOINT 2c92b9e3 (14:31Z) [open] started 14:33Z (relaunch of verify-night-2); branch lane/verify-night-3 @2c92b9e3; reading inbox; queue: x4 equiv d9b3724d/b6f2e1df, +sha256 x4, H100 +blake3, xob
# verify-night-3: non-producer verifier for Table 2 cells (relaunch of verify-night-2, cloud VM)

Brief: `internal/lane-briefs/verify-night-3.md` + `relaunch-branches-0725.md` (branch lane/verify-night-3 cut from
lane/verify-night-2 @ 2c92b9e3). Pod vy-verify-night-3 k2ww8qvkhxlvab (cpu3c 16 vCPU, 150 GB, $0.48/h), 14:32-15:06Z.

## Method
- Verifier tree: lane/verify-night-3 a5d9b632 = main 2c92b9e3 + merge of 5b28557b (blake3-xob scheme + pins); from 14:51Z
  977ad27b (+ reverify reads a proof dir published at the tree root). ligero-verify built on the pod by pod_bootstrap.sh
  (GPU stage fails on a CPU pod, as expected); frozen bench-instances built from the committed seeds.
- `evidence/pod-scripts/`: lib.sh (run's minted custody key as the store remote), 10-equiv.sh (instance_equiv --check +
  tables._equiv_content), 20-reverify.sh (main's reverify per result), 30-summary.py. All runs --custody-r2, all PRESERVED:
  r20260925-143459-f66c (bootstrap), -143942-5ce1 (equiv, fetch error: doc is meta, not payload), -144140-d25e (equiv),
  -143948-2223 (sha256, ERROR layout), -144149-2172 (xob x3), -145113-f083 (fcd6a623), -145803-dd7d (4aa258ee).

## Verdicts
| subject | what | verdict | verdict art |
|---|---|---|---|
| art:d9b3724d | instance-equiv fp8-ada-x4 8192 (for art:6b6d4484 / art:19be6afa) | accepted | art:73aa7efe |
| art:b6f2e1df | instance-equiv fp8-ada-x4 32768 (for art:ecccca50) | accepted | art:7b44bcad |
| art:b47828e4 | fp8-ada+blake3-xob frozen, 49/49, 2^-128.40, sys 3d6cc67b | accepted | art:cc5f72de |
| art:bb69174b | fp8-ada-x4+blake3-xob 4096, 13/13, 2^-128.33, sys f90e7b41 | accepted | art:99a5a9fd |
| art:ecccca50 | fp8-ada-x4+blake3-xob 32768 plateau, 97/97, 2^-128.07 | accepted | art:47cf9051 |
| art:fcd6a623 | bf16-hopper-x4+sha256 8192, 49/49, 2^-128.40, sys a02f283d (977ad27b) | accepted | art:192c1ed9 |
| art:4aa258ee | fp8-hopper-x4+sha256 32768, 97/97, 2^-128.07, sys 6cf20505 (977ad27b) | accepted | art:3b2b8e2f |

- Equiv: --check reproduces every field once the producer tags lane/provenance are dropped; equal=True; candidate == result's
  instances ref. Renderer gap: tables._equiv_content @2c92b9e3 still requires frozen == FROZEN_INSTANCES[target] ([0, 4096]).
- Footnote for every cell verdict: file re-verification (runner's coins), not transferable. Verifier tag is
  ligero-verify(sha256 ...) (synced tree has no .git); the note label names the commit.
- Already done by verify-night-2 (no action): H100 +blake3 c8730574 7c6b4647 9c11326c 7a3965da (and the 75cbbac1 four).
- Not done: 5090 NVFP4 art:70f275ac / art:6740eb22, fail-closed (reverify's commitment recompute has no fp4-nvf4; main change).

## Handoffs
- Received (own inbox): `20260925T1441Z-handoff-from-red-team-standard-hash-2.md`, `20260925T1450Z-handoff-from-red-team-standard-hash-2.md` (resend), `20260925T1453Z-handoff-from-red-team-standard-hash-2.md` (H100 +blake3 class; informational).
- Inherited from verify-night-2 (read at start; the open ones are the queue above): `20260925T0745Z-handoff-from-coordinator.md` `20260925T0800Z-handoff-from-poseidon-v1.md` `20260925T0805Z-handoff-from-red-team-standard-hash.md` `20260925T0835Z-handoff-from-poseidon-v1.md` `20260925T0835Z-handoff-from-red-team-standard-hash.md` `20260925T0840Z-handoff-from-sp1-committed.md` `20260925T0844Z-handoff-from-blake3-80gb.md` `20260925T0850Z-handoff-from-coordinator.md` `20260925T0900Z-handoff-from-poseidon-v1.md` `20260925T0905Z-handoff-from-b-ligero-standard-hash.md` `20260925T0925Z-handoff-from-poseidon-v1.md` `20260925T0935Z-handoff-from-blake3-80gb.md` `20260925T0935Z-handoff-from-coordinator.md` `20260925T0946Z-handoff-from-coordinator.md` `20260925T0958Z-handoff-from-b-ligero-standard-hash.md` `20260925T1003Z-handoff-from-coordinator.md` `20260925T1008Z-handoff-from-b-ligero-standard-hash.md` `20260925T1017Z-handoff-from-coordinator.md` `20260925T1024Z-handoff-from-coordinator.md` `20260925T1027Z-handoff-from-red-team-standard-hash.md` `20260925T1030Z-handoff-from-poseidon-v1.md` `20260925T1033Z-handoff-from-red-team-standard-hash.md` `20260925T1037Z-handoff-from-b-ligero-standard-hash.md` `20260925T1039Z-handoff-from-red-team-standard-hash.md` `20260925T1040Z-handoff-from-coordinator.md` `20260925T1041Z-handoff-from-red-team-standard-hash.md` `20260925T1045Z-handoff-from-blake3-80gb.md` `20260925T1053Z-handoff-from-red-team-standard-hash.md` `20260925T1105Z-handoff-from-coordinator.md` `20260925T1114Z-handoff-from-coordinator.md` `20260925T1124Z-handoff-from-coordinator.md` `20260925T1125Z-handoff-from-b-ligero-standard-hash.md` `20260925T1125Z-handoff-from-coordinator.md` `20260925T1130Z-handoff-from-blake3-80gb.md` `20260925T1142Z-handoff-from-b-ligero-standard-hash.md` `20260925T1146Z-handoff-from-coordinator.md` `20260925T1150Z-handoff-from-b-ligero-sha256.md` `20260925T1150Z-handoff-from-poseidon-v1.md` `20260925T1202Z-handoff-from-b-ligero-sha256.md` `20260925T1202Z-handoff-from-coordinator.md` `20260925T1205Z-handoff-from-poseidon-v1.md` `20260925T1210Z-handoff-from-blake3-80gb.md` `20260925T1220Z-handoff-from-b-ligero-standard-hash.md` `20260925T1226Z-handoff-from-red-team-standard-hash.md` `20260925T1315Z-handoff-from-b-ligero-standard-hash.md`
- Sent: `lanes/coordinator/20260925T1446Z-handoff-from-verify-night-3.md`, `lanes/coordinator/20260925T1507Z-handoff-from-verify-night-3.md` (merge-ready),
  `lanes/red-team-standard-hash-2/20260925T1502Z-handoff-from-verify-night-3.md`, `lanes/red-team-standard-hash-2/20260925T1507Z-handoff-from-verify-night-3.md`.

## FINAL
~~~text
tip: lane/verify-night-3 @ 906255b2 (base lane/verify-night-2@2c92b9e3)        merge-with: lane/b-ligero-standard-hash@5b28557b (merged in)
known-failures: none                                                              pod: terminated 15:06Z; ~$0.30
artifacts: art:73aa7efe art:7b44bcad art:cc5f72de art:99a5a9fd art:47cf9051 art:192c1ed9 art:3b2b8e2f
~~~
7/7 accepted. 977ad27b: reverify reads a proof tree published at its root (the +sha256 x4 trees need it); test 906255b2, reverify_test 10/10.

## Reopen 1 (19:24Z): flock-backend CPU drill-down replay
- Request: `lanes/cell-verifier/20260925T1930Z-handoff-from-coordinator.md` (redirected to me). Confirmation: `20260925T1937Z-handoff-from-coordinator.md`.
- Pod vy-verify-night-3 mzclpkcwdyp4xm (cpu3c 16 vCPU). Inputs art:904398d8 were staged by r20260925-193226-9540. The replay ran as
  r20260925-193306-85c5: `20-pure.sh REL=bf16-hopper MODE=replay` @ cursor/flock-backend-4983 ab5c1156, `--tool flock_pure --custody-r2`.
- **art:827f594c: verified=accepted.** 18/18 sessions REPLAY accepted (p0-1024, p1-2048, p2-4096; 6 each). Instances were regenerated on
  the pod; the lowering da1bbe2c is PINNED. The note says it's a CPU drill-down (rule K) and a file re-verification.
- Sent: `lanes/coordinator/20260925T1926Z-handoff-from-verify-night-3.md` (REOPENED), `lanes/coordinator/20260925T1940Z-handoff-from-verify-night-3.md`.
- Pod terminated 19:39Z, about $0.10.
- Queued, **not taken in this job** (they need a new launch):
  - `20260925T1940Z-handoff-from-coordinator.md`: SHA-256 cells art:ac1f532c and art:675a03a3, plus equivalence documents art:dc455fc8 and art:40b23d0b.
  - `20260925T1945Z-handoff-from-coordinator.md`: the vllm-v1 cell art:f7aac95f and its equivalence document art:d4402d29.

## Reopen 2 (19:42Z): 3 queued cells + the H100 vllm-v1 cell
- Requests: `20260925T1940Z-handoff-from-coordinator.md`, `20260925T1945Z-handoff-from-coordinator.md`, and b-ligero-vllm-v1's
  2010Z (relayed by the coordinator's launch message).
- Pod vy-verify-night-3 p3ink8nhwnomt7 (cpu3c 16 vCPU, 100 GB). Scripts: `evidence/pod-scripts/41-regen.sh`, `42-reverify-tree.sh`,
  `43-round2.sh`. Equivalence evidence: `evidence/equiv/regen-*.json`.
- Runs: r20260925-194914-20b4 and r20260925-201329-502e, both PRESERVED.

| cell | tree | batch | verdict | equiv | equiv verdict |
|---|---|---|---|---|---|
| art:ac1f532c 4090 fp8-ada-x4+sha256 16384 | main 7da00370 | 97/97, 2^-128.31, sys d6b0cd8d | art:833fc972 | art:dc455fc8 (re-derived + --check) | art:388e52d3 |
| art:675a03a3 A100 bf16-ampere-x4+sha256 4096 | main 7da00370 | 25/25, 2^-128.05, sys a862f7a0 | art:19d49495 | art:40b23d0b (arrays regenerated from the frozen set, x/W/y sha256 equal) | art:16c71390 |
| art:f7aac95f 4090 fp8-ada-x4+vllm-v1 16384 | lane/b-ligero-vllm-v1 acd50fec | 97/97, 2^-128.31, sys f7f31613 | art:83483c9f | art:d4402d29 (re-run at acd50fec and 7da00370) | art:7d6d25db |
| art:6d6464d1 H100 fp8-hopper-x4+vllm-v1 32768 | acd50fec | 49/49, 2^-128.20, sys 69054deb | art:c319dee2 | art:9b5f1e24 (re-run at acd50fec) | art:c42c70b9 |

- Sent: `lanes/coordinator/20260925T2023Z-handoff-from-verify-night-3.md`.
- Pod terminated 20:21Z, about $0.30.
- Also received: `20260925T2011Z-handoff-from-b-ligero-vllm-v1.md` (art:6d6464d1 and art:f7aac95f): both answered above.

## Reopen 3 (20:28Z): route (a) live-coin G3
- Request: `lanes/coordinator/20260925T2030Z-handoff-from-route-a-live.md` (via the coordinator's launch message).
- Also received: `20260925T2045Z-handoff-from-coordinator.md` (the H100 pure-Flock label), then `20260925T2050Z-handoff-from-coordinator.md`,
  which CANCELLED it and moved it to verify-flock-pure. Not taken.
- Pod vy-verify-night-3 7qkora4f5oy6t9. Scripts: `evidence/pod-scripts/50-g3-route-a.sh`, `51-g3-statements.sh`, `52-g3-1024-unpinned.sh`.
  Evidence: `evidence/g3-route-a/`.
- Runs: r20260925-203452-5265, r20260925-204110-326f and r20260925-204749-26c6, all PRESERVED.
- **art:3bfb2f58: verified=accepted.** 5/5 sessions pass every gate check except non_producer, including the prime proof and the
  Flock replay. Negatives are rejected.
- **art:d5731679: note only.** The prime commitment at [0, 1024) isn't pinned. It accepts 5/5 with `--allow-unpinned-commitment`.
- Sent: `lanes/coordinator/20260925T2055Z-handoff-from-verify-night-3.md`.
- Pod terminated 20:52Z, about $0.15.

## Reopen 4 (21:38Z): route (a) relabel + H100 keyed-BLAKE3 x4
- Requests: `20260925T2140Z-handoff-from-coordinator.md` and `20260925T2145Z-handoff-from-coordinator.md` (producer:
  `lanes/coordinator/20260925T2112Z-handoff-from-x4-hopper-blake3.md`).
- **art:4b52879f: verified=accepted**, verdict art:317fe4b7. No pod: its 5 proofs are the ones gated in r20260925-204110-326f.
  Evidence: `evidence/g3-route-a/relabel-4b52879f.json`.
- Pod vy-verify-night-3 i86pg3pvzc9vjm (cpu3c 32 vCPU). Run r20260925-214214-f87d at main 78b8935b (`evidence/pod-scripts/60-round4.sh`).
  - art:d88a9948: accepted, verdict art:ea920793.
  - art:5ea60c40: accepted, verdict art:e6b6b5c2.
  - Equivalence art:a400cae2: accepted, verdict art:9d8a1137.
  - Equivalence art:6b27220a: accepted, verdict art:d782b585.
- Sent: `lanes/coordinator/20260925T2210Z-handoff-from-verify-night-3.md`.
- Pod terminated 22:09Z, about $0.50.
- Also received: `20260925T2210Z-handoff-from-route-a-live.md` (relabel art:4b52879f and art:aa9223c2). The coordinator's 2145Z settled the tolerance question. art:4b52879f is accepted, and rederive reproduces it (a note addendum records this). art:aa9223c2 gets a note only (unpinned [0, 1024), as art:d5731679).

## Reopen 5 (22:21Z): route (a) re-registration
- Request: `20260925T2225Z-handoff-from-route-a-live.md` (with the coordinator's launch message: label only art:77411c93).
- **art:77411c93: verified=accepted**, verdict art:eb1a010f. No pod. The 5 proofs are the ones gated in r20260925-204110-326f, and
  sessions equal art:4b52879f's. Only envelope fields changed. Evidence: `evidence/g3-route-a/relabel-77411c93.json`.
- I left art:112afcfa and art:3d7cbea2 unlabelled, as instructed.
- Also received: `20260925T2220Z-handoff-from-coordinator.md` (announces this re-registration). Answered by the art:77411c93 label above.

## Reopen 6 (23:21Z): H100 blake3-xob x4
- Request: the coordinator's launch message, from `lanes/coordinator/20260925T2308Z-handoff-from-x4-hopper-blake3.md`.
- Pod vy-verify-night-3 o2gvkt3wwmn1le (cpu3c 32 vCPU). Run r20260925-232422-96b1 at main 6c3568dc (`evidence/pod-scripts/70-round5.sh`).
  - art:955a52e0: accepted, verdict art:120b459a.
  - art:f15909f5: accepted, verdict art:f8b8836c.
  - Equivalence art:72745743: accepted, verdict art:c43ec491.
  - Equivalence art:04f24f73: accepted, verdict art:835ca8d9.
- Sent: `lanes/red-team-standard-hash-2/20260925T2342Z-handoff-from-verify-night-3.md`, `lanes/coordinator/20260925T2342Z-handoff-from-verify-night-3.md`.
- Pod terminated 23:41Z, about $0.35.
- Also received: `20260925T2335Z-handoff-from-coordinator.md` (the same request). Answered above.

## SP1 below-bar verification (reopened 03:50Z, FINAL 06:36Z)

All nine sp1-evaluator results are `verified=accepted`, `below_bar=true`, with a note. The run is
r20260926-053354-a19b (PRESERVED), from `main` 3d57f08b. The method and the table are in
`lanes/coordinator/20260926T0635Z-handoff-from-verify-night-3.md`; the verdicts are in `evidence/sp1-below-bar/` and the
scripts in `evidence/pod-scripts/80-82*`.

Handoffs received: `20260926T0305Z-handoff-from-coordinator.md`: done, and answered in that handoff.

~~~text
tip: none (no repo commits; verification from main 3d57f08b)        merge-with: none
known-failures: none    pod: vy-verify-night-3 heudtct27whkty terminated 06:31Z (earlier rd921ysua7g60b reaped 04:06Z, jnp5k2d0vy9z2h gone after a failed setup); ~$0.9
artifacts: art:f1d4da61 art:dc494b62 art:47a673f7 art:19a4fdb3 art:095d5306 art:56fa0faf art:34bb8329 art:fd92bd86 art:a38566af
~~~
