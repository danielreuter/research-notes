---
lane: blake3-80gb
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T07:27Z
---

# +blake3 commitment: 18 s -> 0.65 s per 4096-row batch (d5b299ff), and `--commit-per-rep` for the commitment bucket

Your base has my 071e3ef7 (pins). Two later commits on `lane/b-ligero-standard-hash` matter for your hopper cells:

1. **d5b299ff: `leaf_bytes_many`** (`leaf/blake3.py`, used by `hashauth.build_row_tree`). The committer folded each row's chunk
   CVs to its BLAKE3 root one row at a time on single-lane numpy (~21 s of a ~21.5 s commit at 4096 rows; cProfile
   r20260925-070830-b881). Now in lockstep: fp8-ada+blake3 commit **0.65 s** (was 18.0 s) on the 4090, roots unchanged
   (a=2f9ff265..., b=0413c926... in both runs), Python verifier ACCEPT (r20260925-072321-d0e6); blake3_test + core_schema_test
   17 passed (new asserts: leaf_bytes_many == leaf_bytes == the `blake3` package, malformed rows fall back row by row).
   Without it, any per-rep commitment you time on a +blake3 relation is the Python fold, not the scheme.
2. **82453d30 + ad4c3440: `bench-vu --commit-per-rep`** (unshared `included-hash`, `--pipeline >= 2`, CUDA): every rep
   commits its own batch afresh (TABLES.md), measured as `commit.seconds` (median over timed reps), `commit.cold_seconds`,
   `commit.reps`, `commit.row_chain_seconds` / `commit.statement_seconds` (both already inside `t.total`), `e2e.seconds =
   commit.seconds + t.total` -- the names main's `bench.views` reads.

Merge `origin/lane/b-ligero-standard-hash` (tip >= d5b299ff) or cherry-pick d5b299ff. I am producing the fp8-ada (4090) cell;
the H100 lines are yours -- I will not take an H100 pod unless the coordinator asks.
