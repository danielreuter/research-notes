---
lane: sp1-committed
kind: report
created: 2026-09-25T07:00Z
status: open
---

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
