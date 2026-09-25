---
lane: red-team-standard-hash-2
kind: report
created: 2026-09-25T14:31Z
status: open
---

CHECKPOINT c88bb683 (22:51Z) [open] 22:51Z xob hopper x4 GRANTED WITH CONDITIONS (2252Z; art:01d83252, run r20260925-221248-ab04); pod drained; waiting for cell ids (not before verify-night-3)
CHECKPOINT c88bb683 (22:13Z) [open] 22:13Z xob hopper: scans 16:2 + 8:2 running on VM (leaf code = 5b28557b); pod dm92ozi7xllxg8 runs H2/R1/R4 + twin relabel
CHECKPOINT c88bb683 (22:09Z) [open] 22:09Z reopened: blake3-xob hopper class review (775786b7): NOT final
CHECKPOINT c88bb683 (22:06Z) [final] 22:06Z FINAL: vllm-v1 GRANTED (2206Z), labels art:f7aac95f art:6d6464d1; x4 hopper +blake3 plateau labels art:d88a9948 art:5ea60c40 (1932Z grant); xob hopper not granted; no pod; tip c88bb683
CHECKPOINT c88bb683 (22:05Z) [open] 22:05Z vllm-v1 GRANTED WITH CONDITIONS (2206Z); proof_class on art:f7aac95f + art:6d6464d1; art:fe52932e; no pod running; waiting only for x4-hopper-blake3 plateau ids
CHECKPOINT c88bb683 (21:17Z) [open] 21:17Z vllm-v1 e2e done (r20260925-203921-01c9): lane tests pass; H2/R1/R4 refused on fp8-ada-x4 and fp8-hopper-x4; 6 port attacks as expected (ctx swaps caught by reverify only). Pod drained. 8:2 gadget scan (VM) control 19 free; honest pass running
CHECKPOINT 540b3f70 (20:37Z) [open] 20:37Z vllm-v1 code read done (leaf, vllm_tree, hashauth, reverify, Rust vllm_v1.rs): no finding yet; 8:2 gadget scan running on VM; creating pod vy-red-team-sh-2 for tests + H2/R1/R4 + 6 port attacks
CHECKPOINT 540b3f70 (20:32Z) [open] 20:32Z starting vllm-v1 statement review (PR #37 acd50fec; cells art:f7aac95f, art:6d6464d1): NOT final
CHECKPOINT 540b3f70 (20:29Z) [open] 20:29Z bf16-ampere-x4+sha256 GRANTED (2029Z); proof_class on art:675a03a3 + art:ac1f532c; x4 hopper plateau ids pending; vllm-v1 review not started (asked coordinator 2029Z); no pod running; tip 540b3f70
CHECKPOINT 1874b18d (19:56Z) [open] 19:56Z acting on inbox 1940Z (bf16-ampere-x4+sha256 grant; shape 16:2 = scanned at 1441Z, leaf code unchanged to 7da00370) -> pod for H2/R1/R4; 1945Z vllm-v1 review queued next. Still waiting on x4 hopper plateau verified labels
CHECKPOINT 1874b18d (19:31Z) [open] 19:31Z x4 hopper +blake3 GRANTED WITH CONDITIONS (handoff 1932Z; art:a75b03a5, run r20260925-190844-a540); pods terminated (~$0.11). Waiting, no pod, for the plateau cells' verified= labels to write proof_class
CHECKPOINT 1874b18d (19:09Z) [open] 19:09Z blake3 16:2 scan at 9a78cd68: 0 free / 122,596 (control 16); 8:2 running (VM). Pods: nj2awhejyzbrjs + 9ix05r9kmxvoi8 never reachable (host 194.68.245.218), terminated; a5zj4kpsx1l14c (EU-RO-1) runs H2/R1/R4 r20260925-190844-a540
CHECKPOINT 1874b18d (18:24Z) [open] 18:24Z reopened: class review fp8-hopper-x4+blake3 / bf16-hopper-x4+blake3 at x4-hopper-blake3 9a78cd68 (shapes 8:2 / 16:2): NOT final; pod vy-red-team-sh-2 next
CHECKPOINT 1874b18d (18:17Z) [final] 18:17Z FINAL (reopen 2): fp4-nvf4+poseidon2 CLASS GRANTED (COMPLETE_ZK_BACKEND, algebraic); labels on art:70f275ac art:6740eb22; scan art:3808e520 0 effective/199k; H2/R1/R4 refused; pod drained 18:15Z ~$0.05; tip 1874b18d
CHECKPOINT 041ac181 (17:48Z) [open] 17:48Z fp4 scan (VM, torch-free) running: controls decode+sponge show effective free rows; random/zero-scales 0 effective. Creating pod vy-red-team-sh-2 for R1/R4/H2/ZK.
CHECKPOINT 041ac181 (17:38Z) [open] 17:38Z reopened: class review fp4-nvf4+poseidon2 (5090 NVFP4 art:70f275ac/art:6740eb22) at main cd963fd4: NOT final
CHECKPOINT 041ac181 (17:37Z) [final] 17:37Z FINAL (reopen), finish-check rerun after store I/O flake; content as 17:34Z
CHECKPOINT 041ac181 (17:34Z) [final] 17:34Z FINAL (reopen): equiv art:9b5f1e24 + art:c2959a5c verified=accepted; proof_class on 6d067ed3 f4dc0501 4d43ab87 4d151f38; fp4 pair not granted; ligero-hygiene no gap (1727Z); pod drained 17:32Z ~$0.03. Re-shown 1502Z/1150Z inbox items were handled before (store I/O flake)
CHECKPOINT 041ac181 (17:33Z) [final] 17:33Z FINAL (reopen): equiv art:9b5f1e24 + art:c2959a5c reproduce -> verified=accepted; proof_class on 4 H100 +blake3 (6d067ed3 f4dc0501 4d43ab87 4d151f38); fp4 pair not granted (Poseidon2 out of scope); ligero-hygiene review no gap (1727Z); pod drained 17:32Z ~$0.03
CHECKPOINT 041ac181 (17:18Z) [open] 17:18Z pod vy-red-team-sh-2 created (cpu3c 4 vCPU) for instance_equiv --check at main 26848644; labels written on 4 H100 +blake3 (6d067ed3 f4dc0501 4d43ab87 4d151f38); fp4-nvf4 NOT in my grant scope
CHECKPOINT 041ac181 (17:11Z) [open] 17:11Z reopened (non-producer): instance_equiv --check art:9b5f1e24/art:c2959a5c + proof_class on reverify-fp4's 6 cells: NOT final
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

## Reopened 17:11Z (non-producer jobs for reverify-fp4 1706Z and ligero-hygiene 1715Z)

* Received `coordinator/20260925T1706Z-handoff-from-reverify-fp4.md` (forwarded by the coordinator). Pod vy-red-team-sh-2
  (3y8xb1vg96ftqm, cpu3c 4 vCPU) ran 17:17-17:32Z, about $0.03, on main 26848644. `instance_equiv --check` on the raw run-record
  files reproduced both documents: art:9b5f1e24 --vus 32768 (r20260925-172940-9a1a) and art:c2959a5c --vus 8192
  (r20260925-172948-5971). Both runs preserved. Labelled `verified=accepted` by red-team-standard-hash-2.
* proof_class COMPLETE_ZK_BACKEND (ref 1453Z) on art:6d067ed3, art:f4dc0501, art:4d43ab87 and art:4d151f38. Not on
  art:70f275ac or art:6740eb22: fp4-nvf4+hash (Poseidon2) is outside my grants. Handoff coordinator/1733Z.
* Received `coordinator/20260925T1715Z-handoff-from-ligero-hygiene.md`. Code review of cd71b615 and 7c655f86 at 46e0c494: no gap
  (reverify only refuses more; config_for is conservative). Handoff coordinator/1727Z. No pod.

## Reopened 17:38Z: fp4-nvf4+poseidon2 class review (5090 NVFP4 art:70f275ac, art:6740eb22) at main cd963fd4

* Scan `rtsh_fp4_free_rows.py` (commit 1874b18d, torch-free, on the VM). The composed system's sys_id is 8c6d260c, the Rust pin.
  The scan runs a full pass and a decode/sponge-layer pass over 8 families: 199,072 mutations, 0 effective free rows. Both
  controls are detected: `hash.prod3584` dropped makes `hash.prod1349` free, and `hash.a[3].n` dropped makes the pin `a[3].n` free. art:3808e520.
* Pod vy-red-team-sh-2 (a53aqdgs4kru3s, cpu3c 8 vCPU) ran 18:03-18:15Z, about $0.05, drained. Setup run
  r20260925-180655-879e; e2e run r20260925-180824-4a04 (`rtsh_fp4_e2e.py`). Results: H2 24 accepted, 48 and 12 refused; R1 and R4
  refused; ZK: pins are is_end + 16 digest lanes, two ZK proofs are both accepted and disjoint, k > l + t.
* Verdict: CLASS GRANTED WITH CONDITIONS, COMPLETE_ZK_BACKEND in the algebraic-hash class. Handoff coordinator/1818Z. Labels
  proof_class + finding on art:70f275ac and art:6740eb22.
* Branch lane/red-team-standard-hash-2 @ 1874b18d, pushed. Its base 041ac181 predates main's fp4 code: the harnesses import
  it and run on main plus this overlay.

## Reopened 18:24Z: fp8-hopper-x4+blake3 / bf16-hopper-x4+blake3 class review (x4-hopper-blake3 9a78cd68)

* Received `coordinator/20260925T1824Z-handoff-from-x4-hopper-blake3.md` (forwarded by the coordinator).
* BLAKE3 scan on the VM: 16:2 has 0 free rows in 122,596 mutations and 8:2 has 0 in 122,528; the 16:2 control shows 16. art:a75b03a5.
* Pods: nj2awhejyzbrjs and 9ix05r9kmxvoi8 (host 194.68.245.218) never accepted SSH and were terminated. a5zj4kpsx1l14c
  (EU-RO-1) ran r20260925-190844-a540 from 19:08 to 19:31Z and was drained; about $0.11 in total.
  Results: H2 fp8 12 accepted / 24 refused, bf16 24 accepted / 12 refused. R1 and R4 refused on both.
* Verdict: CLASS GRANTED WITH CONDITIONS. Handoff coordinator/1932Z. Plateau labels wait for verification, expected 19:30-20:30Z.
* 19:39Z received `20260925T1940Z-handoff-from-coordinator.md` ("Class grant request: bf16-ampere-x4+sha256"). Acted on it: GRANTED
  WITH CONDITIONS (handoff coordinator/2029Z). Pod y48ucqzibtr5ma ran r20260925-200024-faf4 (setup, R1, R4) and r20260925-201740-b843
  (H2 with synthetic VUs, harness 540b3f70) from 20:00 to 20:28Z, about $0.06, drained. Labels on art:675a03a3 (ref 2029Z) and
  art:ac1f532c (ref 1033Z).
* 19:40Z received `20260925T1945Z-handoff-from-coordinator.md` ("Review request: the new vllm-v1 statement"), plus
  `20260925T2011Z-handoff-from-b-ligero-vllm-v1.md`. Not started: it is a full new-scheme review, so I asked the coordinator
  to confirm (2029Z).
* The x4 hopper +blake3 plateau cells have no ids or verified labels yet (20:28Z).

## 20:32Z: vllm-v1 statement review (PR #37 acd50fec; b-ligero-vllm-v1 1938Z / 2011Z)

* Code read of the leaf, vllm_tree, the hashauth / relchain / reverify vllm branches and the Rust sources: no finding. One nit:
  Python `_verify_vllm` raises on a non-field digest instead of rejecting (fail-closed).
* 8:2 pos_leaf gadget scan on the VM: 0 free rows in 223,604 mutations; controls show 19 and 16. art:fe52932e.
* Pod f2j22l0sij2aak ran r20260925-203921-01c9 from 20:38 to 21:11Z, about $0.13, drained. Lane tests pass; H2, R1 and R4 are
  refused on both relations. Of the 6 port attacks, the ctx swaps are caught only by reverify.
* Verdict: CLASS GRANTED WITH CONDITIONS (handoff coordinator/2206Z). Labels on art:f7aac95f and art:6d6464d1. Harnesses c88bb683.
* 21:37Z received `20260925T2140Z-handoff-from-coordinator.md` ("After the vllm-v1 review: proof_class labels on the H100
  keyed-BLAKE3 x4 cells"). Done at 22:10Z under the 1932Z grant: art:d88a9948 (fp8-hopper-x4+blake3, 65,536 VUs, 2^-128.40) and
  art:5ea60c40 (bf16-hopper-x4+blake3, 16,384 VUs, 2^-128.07). verify-night-3 accepted both from main 78b8935b, which contains
  9a78cd68. The blake3-xob hopper cells were not labelled: no grant covers them.

## 22:09Z: blake3-xob hopper x4 class review (x4-hopper-blake3 775786b7)

* The xob leaf code is byte-identical to 5b28557b. Scans on the VM: 16:2 has 0 free rows in 95,452 mutations and 8:2 has 0 in
  95,384; each control shows 16. art:01d83252.
* Pod dm92ozi7xllxg8 ran r20260925-221248-ab04 from 22:12 to 22:50Z, about $0.15, drained. H2 and the twin relabel (both
  directions) are refused on both relations, and so are R1 and R4.
* Verdict: CLASS GRANTED WITH CONDITIONS (handoff coordinator/2252Z). Labels wait for the cell ids and verify-night-3.
