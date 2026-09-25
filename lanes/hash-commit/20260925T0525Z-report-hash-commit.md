---
lane: hash-commit
kind: report
created: 2026-09-25T05:25Z
brief: coordinator launch message 2026-09-25 05:13Z (LANE-CONTRACT form); kb/TABLES.md "Commitment time counts"
branch: lane/hash-commit (worktree ~/projects/verity-main-wt/hash-commit), base main@c1891d48
final: 13:30Z hard; budget $20
status: open
---

CHECKPOINT 5d14dafa (05:39Z) [open] 4090 fp8-ada l8192 p4 BEFORE (6e1cc576, no cache): commit 2.286s (trees 1.77 chain 0.33 rows 0.18) t.total 0.287 e2e 2.573, rust accepts, ev 247e44ca. tip 5d14dafa (CUDA row_sponge kernel, trees from chain digests) testing+bench now
CHECKPOINT c1891d48 (05:25Z) [open] 05:26Z started; 4090 vy-hash-commit up (Ryzen 7950X), bootstrap running; commit time = host numpy Poseidon2 digests + torch GPU sponge (same digests twice) + py SHA trees; next: commit-reps harness, then CUDA row-sponge committer
# hash-commit: hill-climb the B-Ligero + in-proof hash committer (row digests + trees), 4090 first

Inbox at startup: nothing new.

## Where the commitment time goes (code reading, main c1891d48)
- `bench_vu_rel` times `R.commit_vus(...)` as `relation.hash.commit_seconds` (once per run, before the warm-up; outside t.total).
- `HashedRelationRunner.commit`: (1) `hashauth.load_or_build_trees`: `Poseidon2Leaf.native` = numpy Poseidon2 on the HOST
  (`hash_rows_np` / `permute_np`: steps permutations of all rows in lockstep, ~2k numpy calls per permutation), then per-leaf
  Python framing + hashlib SHA-256 levels (4096 leaves per tree); (2) `hashchain.row_chain` on the device: the same sponges
  again through `permute_torch` (hundreds of small torch kernels per step) for the prover's gathered chain states
  (`sponge_seconds`); (3) host/device copies of digests and rows.
- The Table 2 cells' `commit_seconds`: 4090 1.04 s (art:1abdf12a: ran with `--auth-cache`, trees LOADED, sponge 0.77 s),
  A100 10.0 s (sponge 2.10), H100 BF16 8.31 s (0.88), H100 FP8 4.33 s (0.64), 5090 0.37 s (0.19).

## Pods
- vy-hash-commit hzku0ng1zou8ql: RTX 4090 (reference part), SECURE EU-RO-1, 16 vCPU, host Ryzen 9 7950X, created 05:21Z, guard 90.

## Log
