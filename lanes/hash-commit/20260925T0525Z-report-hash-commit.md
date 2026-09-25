---
lane: hash-commit
kind: report
created: 2026-09-25T05:25Z
brief: coordinator launch message 2026-09-25 05:13Z (LANE-CONTRACT form); kb/TABLES.md "Commitment time counts"
branch: lane/hash-commit (worktree ~/projects/verity-main-wt/hash-commit), base main@c1891d48
final: 13:30Z hard; budget $20
status: open
---

CHECKPOINT b862be30 (06:31Z) [open] commit-gpu (retarget 06:35Z): GPU committer for frame-v3 word / SHA-256-row / keyed-BLAKE3-row leaves + trees, then vllm-v1; target <=5 ms per 4096 instances, byte-identical to core; surveying hash_gpu + leaf/blake3 now
CHECKPOINT b862be30 (06:19Z) [blocked] waiting for the SHA-256/BLAKE3 retarget (0546Z PAUSE). 4090 fp8-ada Poseidon2 committer 2.297->0.035s commit, e2e 2.583->0.321, byte-identical (ev 247e44ca, stmts 897697c9, Rust 25/25); 20 results+trees PRESERVED; pod terminated 06:09Z ~$0.61; handoff coordinator/0612Z
CHECKPOINT b862be30 (05:56Z) [open] 4090 A/B x3 (CREPS5), ev+stmt sha identical all, rust 25/25: base commit 2.295-2.302s e2e 2.58; 5d14dafa (CUDA row_sponge) 0.254-0.258; 0b40ae8a (+SHA prefix) 0.219-0.236 e2e 0.505. rows 0.19 = list->int64; b862be30 passes drawn arrays, A/B now
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
  TERMINATED 06:09Z (49 min x $0.74/h = ~$0.61).

## Log
- 05:38Z BEFORE (tree 6e1cc576 = main's committer + the commit-reps harness, no --auth-cache), 4090 fp8-ada l=8192 p4 reps 5,
  CREPS 3: commit 2.286 s (rows 0.181, trees 1.766 [host numpy Poseidon2 of x+W + SHA], chain 0.330 [torch sponge], host 0.008),
  cold 2.434, t.total 0.287, e2e 2.573; evidence sha 247e44ca…, rep1 .stmt files sha e0e53b61…, Rust batch 25/25 accepted.
- Step 1, 5d14dafa: CUDA `row_sponge` (one thread per committed row, the whole Poseidon2 sponge in registers, the straight-line
  permutation from `permute_ring` like the existing witness kernel) gives the chain states AND the digests once; the W/x trees
  take their leaves from those digests (`hashauth.build_row_tree(digests=)`), no host hash. Kernel JIT inside the runner's
  `__init__` (compile_seconds). Tests (pod): kernel == chain_witness == native for 8/16-bit words and fp4 lanes, permute KAT.
  r1: commit 0.254 s (rows 0.182, trees 0.043, chain 0.018), t.total 0.286, e2e 0.540; evidence sha and stmt sha IDENTICAL, Rust 25/25.
- Step 2, 515ed32a: the 0.18 s `rows` was np.asarray over 2 x 4096 x 1536 Python ints (frozen_instances builds per-VU lists
  from the tier's array('H')). `frozen_instances` now returns a list subclass carrying uint16 views of the tier's arrays
  (what the lists hold, recycled i mod n); commit copies them narrow to the GPU once, widens there, and reuses them as rows_d.
- Step 3, 0b40ae8a: SHA-256 tree leaves / nodes / pads hashed from one per-domain prefix `.copy()` (same bytes; test pins it to
  CommitmentDomain.leaf/.node and the pad leaf), row leaf values serialized in bulk.
- A/B: 30-ab.sh, 3 alternating rounds base / 5d14 / 515e / tip, CREPS 5; intermediate trees = tip minus reverse patch,
  checked by git tree hash.
- 05:55Z A/B result: step 2 did nothing on fp8-ada. Its instance set is SYNTHETIC (drawn per VU, `.tolist()`), not the frozen
  vu-k1536 tier, so rows stayed at 0.19 s. Step 4, b862be30: `instances` keeps the drawn / npz-cached operand arrays
  (`VUs.x_rows`), stacked inside the commit clock; `_instance` is unchanged for its sp1 caller.
- 05:59Z step 4 A/B vs 0b40ae8a (35-ab2.sh, 3 rounds; tests on the tip 34 passed, 1 skipped [the frozen tier isn't built on the pod]).
- 05:46Z coordinator PAUSE (read 05:57Z): Poseidon2 is dropped from Table 2 (SHA-256 / BLAKE3 only). Per it: step 4's A/B
  (already running) finished, every measured run was registered and preserved from the pod (20; 40-register.sh /
  45-register-all.sh), the pod was terminated at 06:09Z, and the handoff is coordinator/20260925T0612Z-handoff-from-hash-commit.md.

## Results (4090 fp8-ada l=8192 p4, medians over alternating rounds; every run evidence 247e44ca…, stmts 897697c9…, Rust 25/25)
| step | commit s | t.total s | e2e s | n | full-tree result (run-files) |
|---|---|---|---|---|---|
| before 6e1cc576 | 2.297 | 0.287 | 2.583 | 4 | art:71a37756 (art:cc2e80a9) |
| 1 5d14dafa row_sponge | 0.254 | 0.286 | 0.540 | 4 | art:4be5c412 (art:2f21f130) |
| 2 515ed32a frozen arrays | 0.247 | 0.287 | 0.534 | 3 | art:381bcee8 (art:1bf9ec97) |
| 3 0b40ae8a SHA prefix | 0.220 | 0.286 | 0.506 | 6 | art:9fdb64e0 (art:2cb60e01) |
| 4 b862be30 drawn arrays | 0.035 | 0.286 | 0.321 | 3 | art:abb219fa (art:13e1c916) |
Other rounds: evidence/registered-4090.txt (slim run-files); all lines: evidence/runs-4090.txt.
