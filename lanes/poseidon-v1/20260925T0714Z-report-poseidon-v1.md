---
lane: poseidon-v1
kind: report
created: 2026-09-25T07:14Z
brief: coordinator launch message (LANE-CONTRACT form); kb/TABLES.md (protocol + Amendments 11:36 / 11:41 PM PT)
branch: lane/poseidon-v1 (worktree ~/projects/verity-main-wt/poseidon-v1), base main@00ffe398
final: 14:30Z hard; budget $30
status: open
---

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
