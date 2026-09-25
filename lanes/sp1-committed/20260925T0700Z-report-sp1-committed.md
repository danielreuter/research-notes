---
lane: sp1-committed
kind: report
created: 2026-09-25T07:00Z
status: open
---

CHECKPOINT cafa9464 (08:18Z) [open] frame-v3 measured r20260925-080516-d8ac: 9/9 negs rejected, 5 reps proved+verified (~4.9s verify), sweep B1024/2048 running. Next: register, build vllm-v1 (build_vllm.sh), vllm measured, same-pod bare baseline.
CHECKPOINT b06a7ec3 (07:59Z) [open] measured fp8-ada frame-v3 run r20260925-073644-5901: 5 reps prove ~52.6s B=4096, 69 shards, 105MB, commit ~8ms, 5/5 pinned verify; sweep in progress. vllm-v1 variant coded+pushed (tip b06a7ec3, main 5631e667 merged); next: pod build+negatives, measured vllm run
CHECKPOINT dcd4eca0 (07:36Z) [open] committed host built (vk 0x009893321b66..3a66, elf f4fc749f; stock identity reproduced); pod: common tests ok incl committed::*, fp8-ada set = art:4a6f7602; exec negatives all rejected (flip-y, sign-of-zero tamper-x @tree a, wrong roots); 215M cycles/4096 VU (hash 54M). launching measured run
CHECKPOINT dcd4eca0 (07:26Z) [open] tip dcd4eca0: committed guest/host/py/vectors + vector_run sp1-committed pushed; pod build r20260925-071747-5eae (stock identity then cuda,relation-committed) running; next: pod cargo tests, executor negatives, measured fp8-ada run
CHECKPOINT 4f1dacb4 (07:18Z) [open] merged main 00ffe398 (core frame-v3 schemas; vectors from core, stand-in dropped); host committed-* cmds + py reference (7 vectors) at 4f1dacb4; pod build r20260925-071747-5eae running; vllm-v1 variant queued after frame-v3 per handoff
CHECKPOINT 1efd4300 (07:04Z) [open] guest feature relation-committed (bare relation + sha256/row/v1 digests via SP1 precompile, frame-v3 tree check) at 1efd4300; pod vy-sp1-committed (4090) bootstrapping stock+committed builds; next host committed-* cmds, py reference
CHECKPOINT 7fcedf47 (06:47Z) [open] started: read contract/TABLES/decision/sp1 kb+reports; PR #15 open, coding against its sha256/row/v1 framing; 4090 pod creating; next: committed guest + host tree check
# sp1-committed report

Lane `sp1-committed`, branch `lane/sp1-committed` in `~/projects/verity-main-wt/sp1-committed`, base main @ 7fcedf47.
Budget $50, FINAL 15:00Z. Goal: an SP1 stock guest proving the full relation on a frozen set with frame-v3 SHA-256 row
leaves (`sha256/row/v1`, PR #15's schema), the host checking the trees natively; bench-result/v1 with the commitment timed.

## Design (07:00Z)

- Guest feature `relation-committed` (its own ELF / vk): reads the bare header and chunks, runs `bare::check_pair` per VU,
  and hashes every x row (role 1) and W column (role 2) with `sha256/row/v1` through the SP1 SHA-256 precompile
  (the workspace's `sha2` patch). The constant 64-byte prefix is absorbed once and the hasher cloned per row (midstate).
- Public values: `"verity/sp1/relation-committed/v1" || u32 format || id || u32 K || u32 B || u8 verdict || y || dx[B] || dw[B]`.
- Host verifier: SP1 verify under the pinned vk, then rebuilds the three frame-v3 trees (a: x-row digests, b: W-column
  digests, y: word leaves `u16`/`u32` big-endian) and compares with the statement's roots. Bindings follow B-Ligero's hashed
  modes (`verity/ligero-b/auth-binding/v2h`, {dataset, tier, manifest_sha256, lo, hi, K, tree, schema}), so every backend
  binding this scheme over a frozen set has the same roots. Kept in one module (`common/src/committed.rs`,
  `verity_sp1/committed.py`) to swap to the core schema when PR #15 merges.
- Commitment bucket: each timed rep first commits the batch natively (row digests + trees, `commit.seconds`), then proves;
  `e2e.seconds = commit.seconds + t.total` (the views' P divides this).
- Line: the RTX 4090 FP8 Ada set (cheapest pod and half the hash blocks of BF16, within the lane's 4090/H100 pod rule).
