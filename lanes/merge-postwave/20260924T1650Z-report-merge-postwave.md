CHECKPOINT 04700cb5 (17:06Z) [open] --source launch killed by guardian disk floor (handoff to coordinator); pods sync running (~100KB/s), setup r20260924-170644-a490 on pod; validate after sync
CHECKPOINT 04700cb5 (16:55Z) [open] render identical to 1540Z except A-GKR hash text; pod vy-merge-postwave (3jmqlddtas1bj3, cpu3c) running validate r20260924-165536-47d1 (py suites + cargo check)
CHECKPOINT 04700cb5 (16:51Z) [open] 5 merges clean (no conflicts), sp1-formats no-op confirmed; A-GKR hash fix 04700cb5; next: laptop render diff + pod cargo check/tests
CHECKPOINT 1b3c7be6 (16:50Z) [open] started; tips match brief; merging main, fill-consumer, agkr-table, sp1-table, sp1-tcdot next
# merge-postwave report

Base: lane/post-wave @ 1b3c7be6. Worktree ~/projects/verity-main-wt/post-wave. Inbox at start: nothing new.

## Log
- Startup: laptop 3.2 GiB free; `research data evict --target-free-gb 8 --runs --dry-run` finds only ~70 MB evictable
  (4.8 GB held back as unpreserved), so no eviction; no laptop builds.
- Branch tips confirmed against the brief: main e7d4a978, fill-consumer 444084d3, agkr-table 5b3a4646, sp1-table 2da1e77e,
  sp1-formats 2b0cc33a, sp1-tcdot 97b5b60a; fill-dc and verify-night at 1b3c7be6.
- Merges (one --no-ff commit each, no conflicts): main 8a885f11->amended, fill-consumer 8ca74b17, agkr-table 356352dd,
  sp1-table 461c9c9f, sp1-tcdot 7d447682. `git merge lane/sp1-formats` after sp1-table: "Already up to date" (no-op confirmed).
- A-GKR hash fix 04700cb5: Table 1 assumptions "BLAKE3 Merkle" -> "SHA-512 Merkle". Source: backends/gkr/gpu/ligero.py
  (MERKLE_HASH = "SHA-512", hashlib.sha512 / sha512_cuda leaves and nodes), verifier/src/verify.rs hash_pair = Sha512,
  proof.rs proof.bin v2 = SHA-512 Merkle, soundness.py. (Fiat–Shamir sponge is SHA-256: gpu/fs_cuda.py, src/transcript.rs;
  the Table 1 text does not name it, so unchanged.)
- Not changed (out of scope, flag for coordinator): drilldown.py's A-GKR rows are stale after agkr-table -- the GPU row still
  says "SHA-256 Merkle (hash_gpu 'sha256')", 2^-127.7, Python-only verifier / Rust Goldilocks-only, and both A-GKR rows say
  "(Table 1's text says BLAKE3 Merkle)", which is no longer true after 04700cb5.
- Clean tree, `git grep -nE '^(<<<<<<<|>>>>>>>|=======)$'` and `rg` both find nothing.
- Render (laptop, merged tree 04700cb5): tables differ from campaigns/morning-tables/render/1540Z-tables.md ONLY in Table 1's
  A-GKR row (BLAKE3 -> SHA-512 Merkle); drilldowns byte-identical to 1540Z-drilldowns.md. Diffs in
  evidence/render-diff-{tables,drilldowns}-vs-1540Z.txt.
- Pod vy-merge-postwave = 3jmqlddtas1bj3 (cpu3c 16 vCPU / 32 GB, 100 GB, $0.48/h), created ~16:55Z; added to machines.toml.
- Laptop at 3.1-3.4 GB free < mem_guardian DISK_FLOOR 3.5 GB: the guardian killed `research run --source .` (0.64 GB while
  archiving; r20260924-165536-47d1 left in phase shipping) and my `research data evict` runs. Handoff to coordinator
  20260924T1702Z. Workaround: `research pods sync` (22 MB launcher; ~100 KB/s ingress, 252 MB tree) + `research run --cwd
  /workspace/src`; setup (toolchains) r20260924-170644-a490 in parallel with the sync.
