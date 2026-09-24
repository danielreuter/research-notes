CHECKPOINT 22741456 (17:56Z) [final] tip 22741456: 6 merges clean + A-GKR SHA-512 fix; cargo checks all pass; numerical 692/1 (pre-existing vocab), research 347/7 (not from merges); render = 1540Z except A-GKR hash; pod terminated 17:56Z
CHECKPOINT 22741456 (17:47Z) [open] tip 22741456: py-numerical 692 pass/1 fail (test_label_keys: included-hash-shared missing from store vocab, pre-existing on base 1b3c7be6); gkr/ligero checks 0; sp1 check running; sp1-common tests rerun fresh target r20260924-174654-7e58
CHECKPOINT none (17:37Z) [open] coordinator handoff: merged main f08314ae -> tip 22741456 (clean; its sp1 diff is comment-only); render at 22741456 identical to 1540Z except A-GKR hash; syncing tip to pod src2 for py suites
CHECKPOINT 04700cb5 (17:36Z) [open] sync done (tree f27d6187 = 04700cb5); SP1 check + relation-bare pass (r20260924-172629-f417), tcdot fork OK, check-tcdot running; validate r20260924-173554-eb0d (py+ligero+gkr)
CHECKPOINT 04700cb5 (17:18Z) [open] SP1 checks running from git-archive of 04700cb5 (r20260924-171410-4069); setup r20260924-171002-37a0; sync ~141/252MB; next: validate.sh (py + ligero + gkr) after sync
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
- Inbox 16:56Z `20260924T1656Z-handoff-steward-guardian.md` ("the laptop guardian killed 1 process(es) of merge-postwave
  (disk floor 3.3GB free): rerun"): acted on -- relaunched through the low-memory path above (launcher 39 MB RSS).
- Pod runs (scripts in evidence/pod-scripts/): setup r20260924-170644-a490 failed rc 127 (`$RESEARCH_RUN_DIR` is not
  shell-expanded in the workload argv; use `bash inputs/X.sh`), setup r20260924-171002-37a0 (apt rc 100 on a stale curl
  security-pool 404 -- curl is on the image, dropped from the list; rustup, sp1up v6.4.0 incl. succinct toolchain, uv OK by
  17:25Z). SP1 checks from `git archive 04700cb5 backends/sp1` (1.2 MB, --send): r20260924-171410-4069 -- check-sp1 and
  check-sp1-bare rc 101 because the succinct toolchain was still downloading (environmental: "override toolchain 'succinct'
  is not installed"), tcdot-fork OK (HEAD 6655716e, tree 4ca5a6ca == FORK_TREE_WIT); rerun of the two checks
  r20260924-172629-f417: check-sp1 0, check-sp1-bare 0. check-tcdot 0 in r20260924-171410-4069 (8m52s, succinct toolchain
  present by then). test-sp1-common there: 81 passed, 4 failed only because the archive lacked repo-root fixtures/
  ("the recorded vector: NotFound"); rerun on the full tree in the tip validate.
- Inbox 17:32Z `20260924T1732Z-handoff-from-coordinator-main-moved.md` (main moved to f08314ae; merge it; guard = 90; laptop
  16 GiB free): acted on -- merged main f08314ae as 22741456 (clean, no conflicts; its backends/sp1 diff is comment-only
  path renames in packed.rs / reduce.rs; nothing under backends/numerical, backends/gkr, backends/ligero-verify changed).
- Render at 22741456 (laptop): same result -- tables differ from 1540Z only in Table 1 A-GKR "BLAKE3 Merkle" -> "SHA-512
  Merkle"; drilldowns byte-identical.
- Tip tree shipped to the pod as /workspace/src2 (pod-side copy of /workspace/src + `research pods sync --dest
  /workspace/src2`, 38 MB diff; .research-source.json commit 22741456 tree d1e72489, dirty false). validate r20260924-173554-eb0d
  ran the older tree 04700cb5 (/workspace/src); the tip validate is r20260924-173844-26c8 (py suites, ligero-verify, gkr,
  gkr babybear, gkr-verify, sp1 host+common+check-model with relation-bare, gkr-verify tests, sp1-common tests).

## FINAL

~~~text
tip: lane/post-wave @ 22741456 (base lane/post-wave@1b3c7be6)        merge-with: none (coordinator fast-forwards main)
known-failures: numerical test_tables.py::test_label_keys_are_the_store_vocabulary (pre-existing on 1b3c7be6); research: 7 (below) | pod: terminated 17:56Z; ~$0.50
artifacts: none (pod runs preserved: r20260924-170644-a490 -171002-37a0 -171410-4069 -172629-f417 -173554-eb0d -173844-26c8 -174654-7e58 -174905-200f -174907-de20)
~~~

Merge commits on lane/post-wave (one each, --no-ff, no conflicts in any):
main e7d4a978 -> a7739031, fill-consumer 444084d3 -> 8ca74b17, agkr-table 5b3a4646 -> 356352dd,
sp1-table 2da1e77e -> 461c9c9f (sp1-formats 2b0cc33a then "Already up to date"), sp1-tcdot 97b5b60a -> 7d447682,
A-GKR hash fix 04700cb5, main f08314ae (coordinator handoff 17:32Z) -> 22741456.

Validation (tip 22741456 unless noted):
- git status clean at the tip; `git grep` / `rg` for `^(<<<<<<<|>>>>>>>|=======)$`: nothing. PASS
- cargo check --release, all rc 0: ligero-verify, verity-gkr (default + babybear), verity-gkr-verify, veritor-zk-host +
  veritor-zk-common + veritor-check-model with relation-bare (r20260924-173844-26c8, tip); veritor-zk-host default and
  relation-bare separately (r20260924-172629-f417, at 04700cb5 -- main's later backends/sp1 diff is comment-only);
  verity-tcdot-host --features stream-operands on the witness-arm fork reproduced from build_fork.sh (HEAD 6655716e, tree ==
  FORK_TREE_WIT; r20260924-171410-4069, at 04700cb5; tcdot/ unchanged since). PASS
- cargo test (extra): verity-gkr-verify ok; veritor-zk-common --features relation-bare 85 passed / 0 failed (r20260924-174654-7e58). PASS
- Python backends/numerical/tests: r20260924-174907-de20 (clean PYTHONPATH): 692 passed, 1 failed, 9 skipped (same as
  r20260924-173844-26c8). PASS except the pre-existing failure test_label_keys_are_the_store_vocabulary: contract.AUTHENTICATION has
  'included-hash-shared' (ligero row sharing, 1054caf3) and research.store.vocab.AUTHENTICATION_VALUES does not -- the same on
  base 1b3c7be6 and on every merged branch, so pre-existing, not from these merges.
- Python tools/research/tests: r20260924-174905-200f (clean PYTHONPATH): 347 passed, 7 failed, 2 skipped. Failing: test_notes
  relaunch, test_pythonpath (pre-existing per coordinator), test_repo_replicas tracked paths, test_store put/fetch + labels
  append-only, test_store_honing evict, test_store_prov shipped source. None of these files is touched by the merges (vs main
  f08314ae the tree differs in tools/research only in pods/health.py, pods/part.py, test_pods_health.py, from the base); the
  pod tree is an rsync copy without .git, which the git-dependent ones need. Not diagnosed one by one: FAIL-not-attributable.
- Render on the laptop at 22741456 vs campaigns/morning-tables/render/1540Z: identical except Table 1 A-GKR assumptions
  "collision-resistant hash (BLAKE3 Merkle)" -> "(SHA-512 Merkle)"; drilldowns byte-identical. PASS

Surprises:
- Harness gotcha: `research run --on` puts its own shipped `research` tool first on PYTHONPATH, so a workload's `pytest
  tools/research/tests` imports /workspace/research/tool/<hash>/research (collection error: no research.pods.health) and
  numerical tests read that copy's store vocab. Run suites with `env -u PYTHONPATH uv run ...`.
- The laptop guardian killed `research run --source` (0.64 GB) under the 3.5 GB disk floor (fixed on main f08314ae:
  streamed ship); `research pods sync` ran at ~100 KB/s (252 MB in 37 min).
- drilldown.py's A-GKR rows are stale after agkr-table (SHA-256 Merkle, 2^-127.7, Python-only verifier, and "Table 1's text
  says BLAKE3 Merkle", now false). Left for a follow-up because the brief scoped the commit to Table 1.
- Pre-existing contract/vocab mismatch on 'included-hash-shared' (above).
Handoffs received: 20260924T1656Z-handoff-steward-guardian.md (acted: relaunched via low-memory path),
20260924T1732Z-handoff-from-coordinator-main-moved.md (acted: merged main f08314ae). Sent: coordinator 20260924T1702Z.
