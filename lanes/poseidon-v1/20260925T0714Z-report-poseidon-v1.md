---
lane: poseidon-v1
kind: report
created: 2026-09-25T07:14Z
brief: coordinator launch message (LANE-CONTRACT form); kb/TABLES.md (protocol + Amendments 11:36 / 11:41 PM PT)
branch: lane/poseidon-v1 (worktree ~/projects/verity-main-wt/poseidon-v1), base main@00ffe398
final: 14:30Z hard; budget $30
status: open
---

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
