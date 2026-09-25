---
lane: poseidon-v1
kind: report
created: 2026-09-25T07:14Z
brief: coordinator launch message (LANE-CONTRACT form); kb/TABLES.md (protocol + Amendments 11:36 / 11:41 PM PT)
branch: lane/poseidon-v1 (worktree ~/projects/verity-main-wt/poseidon-v1), base main@00ffe398
final: 14:30Z hard; budget $30
status: open
---

CHECKPOINT none (12:01Z) [open] A100 re-measured w/ MALLOC (terminated 11:58Z): n4096 (set bound) P=5477 (1.85e7x) commit 0.063s art:ba387d41, BYTEID ok, A/B +0.1%; vn2 handoff 1205Z. 4090 re-measure pod 0d2olfrqxg82q5 syncing. Spend ~$10.
CHECKPOINT none (11:44Z) [open] H100 re-measured w/ MALLOC (Xeon pod, terminated 11:39Z): bf16 plateau n32768 P=10299 art:a250d4b7, fp8 n32768 P=18483 art:752dcde9; same-pod A/B +2.1%/+0.1% at plateau; vn2 handoff 1150Z. A100 re-measure w/ MALLOC on 25b8diy5t3f3tc bootstrapping; 4090 after.
CHECKPOINT none (11:11Z) [open] h100m-bf16hopper (MALLOC set): n65536 P=10066 (dip at 16384 kept the rule open), n131072 running; fp8 + same-pod A/B next. 5090 blocked on main reverify (fp4-nvf4 + FP4Format not recomputed), coordinator informed by vn2.
CHECKPOINT none (10:57Z) [open] H100 re-measure (MALLOC set, Xeon 8470 pod) r20260925-104045-de31: h100m-bf16hopper n32768 P=10299 (EPYC unset run: 10191), rule not yet fired, n65536 running. 5090 laptop preserved 34/34. No new inbox.
CHECKPOINT none (10:35Z) [open] Merged main 3301c435 (steps-pin R1/R2/R4 fix, verify-side only) -> 7ffb7095. vn2 accepted all 4 H100 results at 3301c435. Coordinator handoff 1035Z sent (5 cells). H100 re-measure with MALLOC vars on h94xn599m62w1t (Xeon 8470) bootstrapping; same-pod A/B planned.
CHECKPOINT none (10:27Z) [open] 5090 DONE (MALLOC vars set): plateau n=131072 P=36637 (1.49e7x) commit 0.444s art:6740eb22, BYTEID ok, vn2 handoff 1030Z; A/B vs unset +0.0% at plateau. Coordinator handoff 1035Z lists all 5 cells. Next: H100 rows re-measured with MALLOC vars (new pod).
CHECKPOINT none (10:09Z) [open] 5090 sweep r5090-fp4nvf4 hit its 131072 cap with the stop rule unfired (P 36636 >= 1.02 P(32768)); continuing to 262144+ (r20260925-100932-d810), then re-register (10:06Z ids superseded). Acked 0946Z disk rule: my laptop run dirs < 1 MB, no proofs pulled.
CHECKPOINT none (09:53Z) [open] 5090 pod i1k6ayj2vk65nu up (Ryzen 9950X; SECURE had no stock; 2 stray pods from a retry-loop bug terminated in ~3 min). Bootstrap 1 failed only at the instance-cache stage (fp4 is --relation fp4-nvf4 + included-hash); rerun r20260925-095252-cff3. H100 28/28 preserved.
CHECKPOINT none (09:31Z) [open] H100 DONE (pod terminated 09:19Z): bf16-hopper plateau n=32768 P=10191 (3.16e7x) commit 0.163s art:72e2b0ba; fp8-hopper n=65536 P=18679 (3.45e7x) commit 0.326s art:23528a63; BYTEID ok; handoff vn2 0925Z. 5090: no SECURE stock, retrying COMMUNITY+SECURE.
CHECKPOINT none (09:03Z) [open] 0847Z handoff acted on (main 94b1c4d2 merged, 82adc8a7). H100 bf16-hopper sweep done: plateau n=32768 P=10191/s e2e 3.215s commit 0.163s, N/P 3.16e7, BYTEID IDENTICAL; fp8-hopper sweeping (n4096 P=15498). Registration after both rows.
CHECKPOINT 10996616 (08:37Z) [open] A100 DONE: plateau n=32768 P=5729/s (1.77e7x), commit 0.53s, art:b5a4454f (+n4096 art:289841b1), byteid ok, to verify-night-2; pod terminated. H100 afx80tft4x2ejt syncing. R1/R2 fix: merge when steps-pin lands
CHECKPOINT 756d04d2 (07:59Z) [open] 4090 DONE: plateau n=32768 P=12589/s (8.53e6x), commit 0.389s, art:c8b52ee2 (+n4096 art:d87b4895) preserved, handed to verify-night-2; pod terminated ~$0.56. A100 sweep running (r20260925-075843-60eb)
CHECKPOINT 32f783c5 (07:14Z) [open] 07:15Z started; merged hash-commit 6e1cc576 harness (47485b81); 4090 pod n005v24vgiougo syncing+bootstrap; next: fp8-ada l8192 p4 sweep 1024..32768 w/ commit-reps 5

# poseidon-v1: the five B-Ligero + Poseidon2-per-row full-relation cells under the TABLES.md measurement protocol

Inbox at startup (06:50Z): nothing new.

## What is re-run (the configurations of today's column-2 cells, 0426Z render)
| row | relation / flags | l | p | old cell (t.total only) | old lane |
|---|---|---|---|---|---|
| A100 BF16 | `bf16-ampere --auth included-hash` (frozen vu-k1536) | 16384 | 8 | art:794365d3 0.8965 s | fill-dc |
| H100 BF16 | `bf16-hopper --auth included-hash` | 16384 | 8 | art:271e0e3a 0.5428 s | fill-dc |
| H100 FP8 | `fp8-hopper --auth included-hash` | 16384 | 8 | art:5387c1b5 0.2957 s | fill-dc |
| RTX 4090 FP8 | `fp8-ada --auth included-hash` | 8192 | 4 | art:1abdf12a 0.3474 s | fill-consumer |
| RTX 5090 NVFP4 | `fp4-nvf4+poseidon2 --auth included-hash` | 8192 | 8 | art:99867b4c 0.1387 s | fill-consumer |
All: bench-vu --zk --mode interactive --target -128, K = 1536, sharing none.

## Method
- Tree: lane/poseidon-v1 = main 00ffe398 + merge of lane/hash-commit 6e1cc576 (47485b81): the `--commit-reps` /
  `--commit-evidence` harness (commitment timed as its own bucket, `commit.seconds`, `e2e.seconds`) with MAIN's committer.
- Committer: lane/hash-commit b862be30 (fast Poseidon2 committer) is used only once verify-night-2 accepts it; else main's.
- Per point: `--reps 5` timed after bench-vu's untimed warm-up sub-batch + full pipelined pass; commitment built 1 + 5
  times from scratch (no --auth-cache); rep 1 dumped; producer-side Rust batch check (does not count).
- Sweep: total VUs 1024, 2048, ... until P(n) < 1.02 P(n/4) or OOM (cap 32768); plateau = highest P.
- P = B / e2e.seconds; overhead = N / P with N = spec dense peak / (2K) (Target.native_peak).
- Registration from the pod (evidence/pod-scripts/register.sh): run-files/v1 + bench-result/v1 with meta.protocol and
  meta.sweep (the blocks `bench.views._protocol` reads), --preserve.
- Scripts: evidence/pod-scripts/ (lib.sh, line.py, sweep.sh, register.sh), outputs /workspace/poseidon-v1/.

## Pods
| pod | id | GPU | host | created | terminated | $ |
|---|---|---|---|---|---|---|
| vy-poseidon-v1 | n005v24vgiougo | RTX 4090 (reference) EU-RO-1 SECURE | EPYC 7352 x48 | 07:03Z | | |

## Log
- 07:03Z merged 6e1cc576 (47485b81, pushed); 4090 pod created; sync + bootstrap (RELS=fp8-ada, NS 1024..32768).
- 07:15Z verify-night-2 accepted hash-commit b862be30 (coordinator/20260925T0715Z-handoff-from-verify-night-2.md: art:abb219fa,
  20-run byte identity) before I measured -> merged b862be30 (54ad119d, pushed): COMMITTER = b862be30 for every row.
- 07:16Z bootstrap run r20260925-071613-baa2 BOOTSTRAP_OK (tree 47485b81; sync 708 s via tar); health OK (encode 1.05x,
  matmul 0.99x, quota 13.6 of 48). Tip synced by rsync (20 s).
- 07:19Z row run r20260925-071902-a923 (row.sh r4090-fp8ada fp8-ada 8192 4, cap 32768): sweep + byte identity.
- 07:28Z BYTEID IDENTICAL (4090 fp8-ada n=4096): tip ev 247e44ca stmts e0e53b61 commit 0.058 s; main's committer (src-main =
  47485b81 files) same ev, same stmts, commit 8.56 s on this host. ev/stmts also equal hash-commit's 0612Z runs.
- 07:28Z run r20260925-072829-f5b2 failed rc=127 (cont.sh not yet on the pod, a race in my ship step); relaunched as
  r20260925-072901-ad83: cont.sh r4090-fp8ada 65536..131072 (P still > 1.02 P(n/4) at 32768).
- 07:30Z handoff coordinator/20260925T0730Z-handoff-from-poseidon-v1.md: plateau n > 4096 gets reason I in bench.views
  (synthetic manifest_sha256 depends on n).
- 07:35Z sweep stopped at 65536 (P 12306 < 1.02 x P(16384)); plateau n=32768. 07:40Z registration run r20260925-074006-c1d4
  (register.sh): 7 points + byte-identity tree, all PRESERVED from the pod; laptop `data preserved --mode head` 15/15 rc 0.
- 07:47Z bootstrap run fetched (--all, preserved=yes); every other run has .custody. 07:48Z 4090 pod TERMINATED.
- 07:50Z A100 pod qb68wysl3ejx8b (create did not register it; `pods register --replace` did). Sync 256 s (tar).
- 07:56Z A100 bootstrap r20260925-075623-deac (BENCH_INSTANCES=1: 6 frozen arrays match the manifest) OK; health: encode 0.527 ms,
  matmul 257.6 TFLOP/s, quota 13.6 of 128 (fill-dc's A100 had 27.2 cores).
- 07:58Z A100 row run r20260925-075843-60eb: row.sh a100-bf16ampere bf16-ampere 16384 8 (cap 131072).
- 08:00Z handoff verify-night-2/20260925T0800Z-handoff-from-poseidon-v1.md (4090 plateau + n=4096).

## RTX 4090 FP8 (fp8-ada +hash, l=8192 p4), sweep r4090-fp8ada, committer b862be30, pod n005v24vgiougo (EPYC 7352, quota 13.6)
N = 330e12 / 3072 = 1.074e11 instances/s (spec dense FP8 330 T). Every point: warm, 5 timed runs, contended false, Rust batch accept.
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|
| 1024 | 9326 | 0.1098 | 0.0875 | 0.0223 (0.140) | 1.15e7 | art:0a1088ad | art:07f7b45c slim |
| 2048 | 10776 | 0.1901 | 0.1555 | 0.0346 (0.136) | 9.97e6 | art:4788fbf3 | art:dc803769 slim |
| 4096 | 11664 | 0.3512 | 0.2932 | 0.0579 (0.162) | 9.21e6 | art:d87b4895 | art:c24671ee full |
| 8192 | 11759 | 0.6967 | 0.5918 | 0.1048 (0.209) | 9.14e6 | art:1d7fdfac | art:e69184ff slim |
| 16384 | 12339 | 1.3278 | 1.1265 | 0.2013 (0.312) | 8.71e6 | art:e817acaa | art:b45f3810 slim |
| **32768 plateau** | **12589** | 2.6029 | 2.2138 | 0.3892 (0.535) | **8.53e6** | **art:c8b52ee2** | art:30f6e8db full |
| 65536 | 12306 | 5.3257 | 4.5444 | 0.7813 (0.909) | 8.73e6 | art:c6516158 | art:6f4c8bd4 slim |
Byte identity at 4096 vs main's committer: IDENTICAL (ev 247e44ca, stmts e0e53b61; main's commit 8.56 s), tree art:26127a90.
Old cell art:1abdf12a: t.total 0.3474 s at 4096 (9.1e6x proving only, no commitment, not warm-protocol).
Pod: 07:03-07:48Z, $0.74/h, ~$0.56.

## A100 BF16 (bf16-ampere +hash, l=16384 p8), sweep a100-bf16ampere, committer b862be30, pod qb68wysl3ejx8b (EPYC 7742, quota 13.6)
N = 312e12 / 3072 = 1.016e11 /s. Every point warm, 5 timed runs, contended false, Rust accept. n > 4096 = the frozen 4096 recycled
(i mod 4096; flagged to the coordinator).
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|
| 1024 | 4129 | 0.2480 | 0.2017 | 0.0462 (0.149) | 2.46e7 | art:3c472d8f | art:0d4741e7 slim |
| 2048 | 4950 | 0.4137 | 0.3549 | 0.0587 (0.139) | 2.05e7 | art:c833eef0 | art:e3171c7e slim |
| 4096 | 5380 | 0.7613 | 0.6813 | 0.0800 (0.158) | 1.89e7 | art:289841b1 | art:decbf2b3 full |
| 8192 | 5507 | 1.4875 | 1.3395 | 0.1480 (0.231) | 1.84e7 | art:0dab1f58 | art:c9507331 slim |
| 16384 | 5632 | 2.9091 | 2.6454 | 0.2637 (0.348) | 1.80e7 | art:b035214a | art:8c28b17b slim |
| **32768 plateau** | **5729** | 5.7200 | 5.1900 | 0.5300 (0.639) | **1.77e7** | **art:b5a4454f** | art:da6298bf full |
| 65536 | 5701 | 11.4959 | 10.4961 | 0.9998 (1.188) | 1.78e7 | art:ee9859ec | art:d7e0259c slim |
Byte identity at 4096 vs main's committer: IDENTICAL (ev 71b51d0b, stmts d54de18b; main's commit 15.8 s), tree art:c8e71ffe.
Old cell art:794365d3: t.total 0.8965 s at 4096 (host EPYC 7713). Runs: bootstrap r20260925-075623-deac, row r20260925-075843-60eb,
register r20260925-082255-9c25 (all .custody). Laptop `data preserved` batch 1 rc 0. Pod 07:50-08:28Z, $1.59/h, ~$1.01.
Handoff verify-night-2/20260925T0835Z-handoff-from-poseidon-v1.md.
- 08:30Z H100 pod afx80tft4x2ejt (EU-FR-1, EPYC 9554, quota 23.8; registered by hand again). First sync died at 41 MB (my
  shell dropped it); re-run 424 s. Bootstrap r20260925-083905-f7cb OK (encode 0.285 ms, matmul 670.8 TFLOP/s).
- Inbox 0745Z (coordinator): R1/R2 red-team SH FAIL affects every included-hash statement; keep measuring, merge
  ligero-steps-pin's fix when it lands ("steps pin + R1/R2 ready"); results count only after fix + re-verify. The fix is
  verifier-side (derive the triple from vu_index, recompute roots); honest unshared proofs are unchanged. Not landed by 09:00Z.
- Inbox 0847Z (coordinator): merge origin/main 58b113bc (commit-gpu) before the next measured runs. The first H100 run
  (r20260925-084727-933f, tree 54ad119d) had just started: killed after 2 points (not registered), merged origin/main 94b1c4d2
  (82adc8a7, pushed; main includes b862be30, so the Poseidon2 committer is the same code path), regenerated
  rev-to-47485b81.patch (backends/direct/ligero + backends/shared; 7 files sha-checked), re-synced (rsync 18 s). A relaunch
  (r20260925-085219-9b19) shipped a stale h100.sh (committer label) and was killed within seconds; final H100 run
  r20260925-085254-6706 (h100.sh: both rows, then register both). Commitment evidence at n=1024/2048 equals the killed run's.
- main PR #19 (in 94b1c4d2): bench.views counts synthetic stream points above 4096 (answers my 0730Z question) but rejects the
  A100 repeats beyond 4096 (I). So the A100 cell candidate is n=4096: registered art:af0089920b38b6e8c7dd2d51c93da51ee2e93abd4ee479880b8027b9113ab1ad
  = the same run and tree as art:289841b1 with meta.sweep a100-bf16ampere-frozen4096 (points 1024/2048/4096, plateau 4096,
  rule: bounded by the set; the repeat points listed under also_measured). Handoff verify-night-2/20260925T0900Z.

## H100 BF16 (bf16-hopper +hash, l=16384 p8), sweep h100-bf16hopper, committer main 58b113bc (b862be30 + commit-gpu), tree 82adc8a7
Pod afx80tft4x2ejt (H100 80GB HBM3, EU-FR-1, EPYC 9554, quota 23.8), run r20260925-085254-6706 (sweeps + registration, rc 0).
N = 989e12 / 3072 = 3.219e11 /s. Every point warm, 5 timed runs, contended false, Rust batch accept. Synthetic instances (no repeats).
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|
| 1024 | 7057 | 0.1451 | 0.1145 | 0.0306 (0.141) | 4.56e7 | art:195b2b4c | art:c05a5cc3 slim |
| 2048 | 8345 | 0.2454 | 0.2117 | 0.0337 (0.150) | 3.86e7 | art:c1f3cb5d | art:0b86bd44 slim |
| 4096 | 9304 | 0.4403 | 0.3974 | 0.0429 (0.147) | 3.46e7 | art:f25486f6 | art:08487b4a full |
| 8192 | 10057 | 0.8146 | 0.7549 | 0.0597 (0.162) | 3.20e7 | art:e79c1dd9 | art:786988ae slim |
| 16384 | 10090 | 1.6238 | 1.4960 | 0.1278 (0.206) | 3.19e7 | art:1bb3dfb6 | art:92ff4ab3 slim |
| **32768 plateau** | **10191** | 3.2153 | 3.0526 | 0.1627 (0.289) | **3.16e7** | **art:72e2b0ba** | art:7d835b9a full |
Stop: P(32768) < 1.02 P(8192). Byte identity at 4096 vs main's pre-b862be30 committer: IDENTICAL (ev 55f3f247, stmts 248b4a6f;
main's commit 7.15 s), tree art:67c3d209. Old cell art:271e0e3a: t.total 0.5428 s at 4096 (proving only).

## H100 FP8 (fp8-hopper +hash, l=16384 p8), sweep h100-fp8hopper, same pod / run / tree / committer
N = 1979e12 / 3072 = 6.442e11 /s. Every point warm, 5 timed runs, contended false, Rust batch accept.
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|
| 1024 | 10701 | 0.0957 | 0.0782 | 0.0175 (0.210) | 6.02e7 | art:b92bcad3 | art:f32e4ffc slim |
| 2048 | 13900 | 0.1473 | 0.1253 | 0.0220 (0.150) | 4.63e7 | art:32131c66 | art:5ae6b1e3 slim |
| 4096 | 15498 | 0.2643 | 0.2328 | 0.0314 (0.157) | 4.16e7 | art:6c512437 | art:3e601d71 full |
| 8192 | 17974 | 0.4558 | 0.4083 | 0.0475 (0.174) | 3.58e7 | art:1c271407 | art:0105c19d slim |
| 16384 | 18443 | 0.8883 | 0.8052 | 0.0831 (0.194) | 3.49e7 | art:b6bab7be | art:fdb9da3b slim |
| 32768 | 18468 | 1.7743 | 1.6222 | 0.1521 (0.270) | 3.49e7 | art:23a524e4 | art:ab3ebe71 slim |
| **65536 plateau** | **18679** | 3.5085 | 3.1820 | 0.3264 (0.476) | **3.45e7** | **art:23528a63** | art:29a6bee7 full |
Stop: P(65536) < 1.02 P(16384). Byte identity at 4096: IDENTICAL (ev 8bc47402, stmts 2c931ab4; main's commit 3.30 s), tree
art:7e6a93cf. Old cell art:5387c1b5: t.total 0.2957 s at 4096. H100 pod 08:28-09:19Z, $3.49/h, ~$2.97. Evidence evidence/h100/.
Handoff verify-night-2/20260925T0925Z-handoff-from-poseidon-v1.md (both plateaus + both n=4096).
- 09:10Z verify-night-2 checkpoint: my 4 results (4090/A100 n=4096 + 32768) all checks PASS; relabeling incl. art:af008992.
- 09:20Z RTX 5090 pod requested.
- 09:3xZ laptop `data preserved --mode head` on the 28 H100 artifacts: 4 batches rc 0, 28/28 PRESERVED. Renderer check on the
  bf16-hopper plateau meta: `views.instance_range` -> ('stream', None), `views._protocol` -> None.
- 09:20-09:31Z 5090: SECURE had no stock (HTTP 500 x6). My retry loop misread a successful COMMUNITY create as a failure and
  created 3 pods (cdsbrseysgi0rh CA $0.69, 4opwt5mylvd9qr $0.69, i1k6ayj2vk65nu $0.99) before I killed it: the first two
  terminated within ~3 min (~$0.07). Kept i1k6ayj2vk65nu (RTX 5090 32 GB, Ryzen 9 9950X; registered by hand). Sync by tar.
- 09:40Z verify-night-2 (poseidon-v1/20260925T0940Z): all 5 accepted: art:d87b4895 (verdict art:66b0d958), art:af008992
  (art:9a29580b), art:289841b1 (art:a4c00776), art:c8b52ee2 (art:2c83448c), art:b5a4454f (art:258c8dd3). H100 on r20260925-093931-f022.
- 09:46Z coordinator: laptop disk below 3 GiB, no laptop downloads/builds. My laptop run dirs total < 1 MB (no proofs pulled);
  no cargo target in my worktree.
- 09:46Z 5090 bootstrap r20260925-094555-c066 failed at the instance-cache stage only (`RELS=fp4-nvf4+poseidon2` is not a
  run.py relation: the row is `--relation fp4-nvf4 --auth included-hash`, fp4/hashed.py); r20260925-095252-cff3 (no RELS)
  BOOTSTRAP_OK: encode 0.187 ms, matmul bf16 238.7 TFLOP/s, PCIe x8 of x16, no 5090 health reference.
- 09:54Z 5090 row run r20260925-095432-4465: r5090.sh (row.sh r5090-fp4nvf4 fp4-nvf4 8192 8, cap 131072, then register).
- 10:06Z first 5090 sweep r5090-fp4nvf4 (run r20260925-095432-4465, registered + preserved from the pod): P 24330 / 27793 /
  31433 / 33753 / 35237 / 35479 / 36462 / 36636 at n = 1024 ... 131072; BYTEID IDENTICAL (ev 1829c793); it ended at its 131072
  cap with the stop rule unfired (36636 >= 1.02 x 35479), so it is NOT a finished sweep. Its ids (plateau art:e0da2cab...,
  tree art:ea6e0378) are not handed off. Continuation r20260925-100932-d810 started 10:09Z, killed within 1 min (no point).
- Inbox 1003Z (coordinator): MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 in every measured run from now. Acted:
  lib.sh records both in each point's meta.txt, register.sh copies them into meta.protocol.malloc_env; the 5090 row is
  re-measured from 1024 as a NEW sweep r5090m-fp4nvf4 with both set (r5090m.sh, run r20260925-101124-095a, cap 1048576).
  The r5090-fp4nvf4 points (unset) then serve as an A/B on the same pod.

## RTX 5090 NVFP4 (fp4-nvf4 --auth included-hash = fp4-nvf4+poseidon2, l=8192 p8), sweep r5090m-fp4nvf4, MALLOC vars set
Pod i1k6ayj2vk65nu (RTX 5090 32 GB, Ryzen 9 9950X, PCIe x8), run r20260925-101124-095a, tree 82adc8a7, committer main 58b113bc.
N = 1676e12 / 3072 = 5.456e11 /s. Every point warm, 5 timed runs, contended false, Rust batch accept, malloc_env recorded.
Last column: the same point in the malloc-unset sweep r5090-fp4nvf4 on the same pod (A/B).
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree | unset P (m vs unset) |
|---|---|---|---|---|---|---|---|---|
| 1024 | 24157 | 0.0424 | 0.0359 | 0.0065 (0.071) | 2.26e7 | art:b349198e | art:da02fd25 slim | 24330 (-0.7%) |
| 2048 | 28930 | 0.0708 | 0.0600 | 0.0108 (0.072) | 1.89e7 | art:647aff38 | art:181892cc slim | 27793 (+4.1%) |
| 4096 | 32428 | 0.1263 | 0.1103 | 0.0160 (0.066) | 1.68e7 | art:70f275ac | art:d8a0d856 full | 31433 (+3.2%) |
| 8192 | 34308 | 0.2388 | 0.2094 | 0.0294 (0.068) | 1.59e7 | art:3aa1f51a | art:5471efc7 slim | 33753 (+1.6%) |
| 16384 | 35458 | 0.4621 | 0.4053 | 0.0568 (0.095) | 1.54e7 | art:a2b8c472 | art:98f20582 slim | 35237 (+0.6%) |
| 32768 | 36182 | 0.9056 | 0.7949 | 0.1107 (0.152) | 1.51e7 | art:466875a2 | art:ec065971 slim | 35479 (+2.0%) |
| 65536 | 36489 | 1.7960 | 1.5717 | 0.2243 (0.273) | 1.50e7 | art:08c4ae96 | art:fcc00dec slim | 36462 (+0.1%) |
| **131072 plateau** | **36637** | 3.5776 | 3.1334 | 0.4442 (0.494) | **1.49e7** | **art:6740eb22** | art:dcef74f1 full | 36636 (+0.0%) |
Stop: P(131072) < 1.02 P(32768). Byte identity at 4096: IDENTICAL (ev 1829c793, stmts 15cd70b9; main's commit 1.108 s), tree
art:4e704415. Commit evidence and statements are identical between the two sweeps at every point checked (1024, 4096).
Renderer check on the plateau meta: instance_range ('stream', None), _protocol None. Old cell art:99867b4c: t.total 0.1387 s
at 4096. Pod 09:31-10:25Z, $0.99/h, ~$0.89 (+ ~$0.07 for the two stray pods). Evidence evidence/5090/.
Handoff verify-night-2/20260925T1030Z-handoff-from-poseidon-v1.md.
- 10:25Z verify-night-2 (poseidon-v1/20260925T1030Z): the 4 H100 results accepted at main 3301c435 (ligero-verify 596529d2 +
  reverify R1/R2/R4): art:72e2b0ba verdict art:31e5458f, art:23528a63 art:181ccbdb, art:f25486f6 art:87ddb393, art:6c512437 art:55208f00.
- 10:28Z main 3301c435 = ligero-steps-pin c8a16e2b (steps pin + R1 layout + R2 commitment recompute + R4 coverage). Merged into
  the lane: 7ffb7095 (pushed). Prover-side for unshared relations: nothing changes (hashauth.layout_error is verify-only; the
  relchain change touches SharedHashedRunner only; serialize changes are read-side), so earlier proofs stand. Regenerated
  rev-to-47485b81.patch (15 files, 2683 lines; 10 files sha-checked); `git apply --check` on the tip OK.
- 10:35Z coordinator handoff coordinator/20260925T1035Z-handoff-from-poseidon-v1.md: all 5 cells + malloc A/B + plan.
- 10:30Z H100 pod h94xn599m62w1t (US, Intel Xeon Platinum 8470 -- not the EPYC 9554 of afx80tft4x2ejt; registered by hand);
  sync 158 s; bootstrap r20260925-103452-4df9. Plan (h100m.sh): fresh sweeps h100m-bf16hopper / h100m-fp8hopper with the MALLOC
  vars set (cap 1048576), then ab.sh: the same pod with the vars unset at n=4096 and each plateau (same-host A/B), then register.
- 5090 laptop `data preserved`: 5 batches running (21/34 PRESERVED so far, every batch rc 0).
- 10:56Z verify-night-2 (poseidon-v1/20260925T1100Z): the 5090 results are NOT re-verifiable at main: reverify.committed_trees
  (R2 recompute) calls relations.relation('fp4-nvf4') (unknown; fp4 lives in fp4/hashed.py FP4_HASHED) and would then refuse
  anyway, because the relation has a lane `hash_format` (FP4Format), which committed_trees does not recompute. Their own checks
  pass: 04 BOUND, 06 ROOTS-MATCH, 05 negatives, base ACCEPT 13/13. No label. Main change needed (reverify: fp4-nvf4 +
  FP4Format trees); the coordinator is told. I'll offer to write it.

## H100 re-measured with MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12 (sweeps h100m-bf16hopper / h100m-fp8hopper)
Pod h94xn599m62w1t (H100 80GB HBM3, US, Intel Xeon Platinum 8470), run r20260925-104045-de31, tree 7ffb7095 (main 3301c435),
committer main (b862be30 + commit-gpu). Every point warm, 5 timed runs, contended false, Rust batch accept, malloc_env recorded.
| sweep | n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|---|
| bf16 | 1024 | 6948 | 0.1474 | 0.1183 | 0.0290 (13.62, first CUDA build) | 4.63e7 | art:3ea21d9f | art:b26b95a5 slim |
| bf16 | 2048 | 8282 | 0.2473 | 0.2140 | 0.0333 (0.131) | 3.89e7 | art:ce89df19 | art:86ba19c3 slim |
| bf16 | 4096 | 9231 | 0.4437 | 0.4017 | 0.0420 (0.120) | 3.49e7 | art:a4499799 | art:0c45644d full |
| bf16 | 8192 | 9762 | 0.8392 | 0.7808 | 0.0584 (0.115) | 3.30e7 | art:d249a75c | art:0442d841 slim |
| bf16 | 16384 | 9700 | 1.6892 | 1.5958 | 0.0933 (0.173) | 3.32e7 | art:e2e30928 | art:f5da2278 slim |
| bf16 | **32768 plateau** | **10299** | 3.1817 | 3.0228 | 0.1590 (0.216) | **3.13e7** | **art:a250d4b7** | art:5838a96f full |
| bf16 | 65536 | 10066 | 6.5104 | 6.1830 | 0.3274 (0.390) | 3.20e7 | art:d291dbaa | art:b7a14b69 slim |
| bf16 | 131072 | 9765 | 13.4227 | 12.7769 | 0.6458 (0.708) | 3.30e7 | art:a567e8f6 | art:1963cf92 slim |
| fp8 | 1024 | 11092 | 0.0923 | 0.0748 | 0.0176 (0.171) | 5.81e7 | art:1dbfd2db | art:000607c8 slim |
| fp8 | 2048 | 13422 | 0.1526 | 0.1309 | 0.0217 (0.108) | 4.80e7 | art:e159ef91 | art:2557708f slim |
| fp8 | 4096 | 15617 | 0.2623 | 0.2322 | 0.0301 (0.101) | 4.13e7 | art:279b8685 | art:9a2f94e0 full |
| fp8 | 8192 | 17112 | 0.4787 | 0.4314 | 0.0473 (0.102) | 3.76e7 | art:28226c47 | art:98d95ee2 slim |
| fp8 | 16384 | 18046 | 0.9079 | 0.8281 | 0.0798 (0.136) | 3.57e7 | art:23705ef7 | art:0824d5b8 slim |
| fp8 | **32768 plateau** | **18483** | 1.7729 | 1.6234 | 0.1495 (0.207) | **3.49e7** | **art:752dcde9** | art:6916a8dd full |
| fp8 | 65536 | 18054 | 3.6299 | 3.3345 | 0.2954 (0.359) | 3.57e7 | art:e31589ce | art:0734e08b slim |
Stops: bf16 P(131072) < 1.02 P(32768) (the n=16384 dip kept it open at 65536); fp8 P(65536) < 1.02 P(16384). BYTEID IDENTICAL on
both (evidence trees art:a4a648a5, art:bf7f2e6c). Same-pod A/B (ab.sh, vars unset, one 5-rep run each): bf16 n=4096 9199
(set +0.3 %), n=32768 10086 (set +2.1 %); fp8 n=4096 15541 (+0.5 %), n=32768 18457 (+0.1 %). Commit evidence and statements
are identical set vs unset. Against the EPYC 9554 pod (unset): bf16 plateau +1.1 %, fp8 plateau -1.0 % (different hosts).
Pod 10:30-11:39Z, $3.49/h, ~$4.01. Evidence evidence/h100m/. Handoff verify-night-2/20260925T1150Z-handoff-from-poseidon-v1.md.
- Decision: the bf16 plateau moved by +2.1 % on the same pod, which meets my 2 % rule (noise is about 1-2 %), so the A100 and 4090 are
  re-measured with the vars set too. A100 pod 25b8diy5t3f3tc (US, EPYC 7742 like the first A100 pod) created 11:41Z; a100m.sh
  caps the sweep at the frozen set's 4096 (RULE_EXTRA names the bound in meta.sweep.rule).

## A100 re-measured with the MALLOC vars (sweep a100m-bf16ampere, capped at the frozen set's 4096)
Pod 25b8diy5t3f3tc (A100-SXM4-80GB, US, EPYC 7742), run r20260925-115155-e772, tree 7ffb7095. N = 1.016e11 /s.
| n | P /s | e2e s | t.total s | commit s (cold) | N/P | result | tree |
|---|---|---|---|---|---|---|---|
| 1024 | 4236 | 0.2418 | 0.1990 | 0.0427 (17.03, first CUDA build) | 2.40e7 | art:266c210f | art:b5d2f09a slim |
| 2048 | 4933 | 0.4152 | 0.3656 | 0.0496 (0.192) | 2.06e7 | art:9d808b33 | art:37f52bc5 slim |
| **4096 plateau (set bound)** | **5477** | 0.7479 | 0.6848 | 0.0630 (0.222) | **1.85e7** | **art:ba387d41** | art:5eb0b2cc full |
BYTEID IDENTICAL (ev 71b51d0b, stmts d54de18b; main's commit 16.05 s), tree art:ab442c56. Same-pod A/B at 4096: unset 5470
(set +0.1 %). Against the first A100 pod (unset, same CPU model): 5380 -> 5477 (+1.8 %, t.total 0.681 -> 0.685 s, commit 0.080 ->
0.063 s). Pod 11:41-11:58Z, $1.59/h, ~$0.45. Evidence evidence/a100m/. Handoff verify-night-2/20260925T1205Z.
- 11:59Z RTX 4090 pod 0d2olfrqxg82q5 (US, EPYC 7642, $0.74/h; registered by hand); syncing.
