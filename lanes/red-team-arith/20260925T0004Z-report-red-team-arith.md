---
lane: red-team-arith
kind: report
created: 2026-09-25T00:04Z
status: final
---

CHECKPOINT none (01:52Z) [final] red-team arith: PASS. 9d1a7f15 0baefa9d f550fdc6 92ea2531/92dab0ad leave proof bytes identical to main 22741456 under fixed coins on 5090, H100, A100 (bare, +hash, FS); robustness: quad_v4/lincomb2 >48KiB smem launch failure, not a byte change; pods terminated, ~$4.07
CHECKPOINT none (01:19Z) [open] H100 done: tests PASS, byte A/B all 6 trees IDENTICAL on fp8/bf16-hopper-v3x4 l4096 p8, +hash (fp8/bf16 l16384), FS; control differs; 9 arts preserved (art:6f099c8b ...); pod terminated 01:16Z (~$3.37). A100 up, run r20260925-011824-1c9a
CHECKPOINT 4bd6c54c (00:55Z) [open] H100 (sm_90, vy-red-team-arith-h100 EUR-IS-3): tests_fused_test PASS, redteam 227 PASS + same 3 smem launch errors (robustness, old kernels OK); byte A/B h8/h16 running r20260925-004904-c8a2 (laptop->pod sync too slow: shipped a 3.6 MB git-archive subset)
CHECKPOINT a4333dd0 (00:35Z) [open] 5090 (sm_120) done: tests_fused_test PASS; byte A/B all 6 trees IDENTICAL on fp4-nvf4 l8192 p8 bare, +hash, FS; seed control differs; art:34e47954 art:35fdf2ab art:75a715b5 art:4d2a8176 art:25e89894; H100 syncing
CHECKPOINT none (00:04Z) [open] read diffs (lincomb2 staging, beta removal, intt_rows, quad_v4); wrote adversarial tests + det-urandom A/B runner (0be285a9); 5090 pod vy-red-team-arith up, bootstrap+tests+A/B running r20260925-000238-66aa
# red-team-arith: independent check that lane/arith 92dab0ad leaves the proof bytes unchanged

Request: lanes/coordinator/20260924T2340Z-handoff-from-arith.md (read at start). Inbox at startup: nothing new.
Branch lane/red-team-arith (worktree ~/projects/verity-main-wt/red-team-arith), base lane/arith@92dab0ad (main 22741456 +
arith's 5 commits). Budget $6, FINAL 03:30Z. All pods created by this lane; nothing of arith's reused.

## Method
- Code read (`git diff 22741456 92dab0ad -- backends/direct/ligero`), findings in "Code review" below.
- Adversarial micro-tests, `backends/direct/ligero/redteam_arith_test.py` (commits 0be285a9, a4333dd0): lincomb2 with int64
  coefficients over the whole int64 range (INT64_MIN/MAX, -P, P, 2P-1, +-2^62, +-2^32 ...), row-strided C1 like
  `r = x[:, :M]`, R2 in {0, 1, R/2, R-1, R}, R around the 1024-row chunk, D in {1, 2, 6, 7}, all-(p-1) inputs, prover-sized
  shapes (R 22730-40000, cols 4096-16384); quad_v4 with sides of 0..70 terms, all p-1, ragged Q, split counts 1/3/1000,
  Q up to 300000; intt_rows at every power of two up to 2^17 (those the device's opt-in shared memory admits), and
  `protocol._intt_ginv` against the pre-change expression; reduce_partial with S up to 512 all p-1; first use of lincomb2 /
  intt_scaled inside a CUDA-graph capture. Reference: plain torch int64 (every product reduced), plus the replaced kernels.
  Plus arith's `tests_fused_test.py` (bit-exact vs the old kernels).
- End-to-end byte A/B, `backends/direct/ligero/redteam_arith_det.py` + `evidence/pod-scripts/rta-pod.sh`: every os.urandom
  draw (verifier coins, mask keys) made deterministic, keyed by (sub-batch, draw number) and restarted at every
  `pipeline.prove_many` pass, so the warm-up passes (their count changed in 92dab0ad) do not shift the recorded rep. One
  tree per commit (22741456, 9d1a7f15, 0baefa9d, f550fdc6, 92ea2531, tip = 92dab0ad + only this lane's two new files):
  hard-linked copies of the synced tip tree with the 4 changed prover files taken from `git show REV:...`. Same pod, same
  frozen instances, the row's Table 2 config (K = 1536, B = 4096, --zk interactive, target -128), `--reps 1 --dump-reps 1`.
  Compared: sha256 of every .stmt/.proof/.hproof/.coins and system.bin of the rep-1 dump. Every run also passes the
  Python verifier (bench-vu asserts it) and the tip dump is re-verified by the pod-built Rust ligero-verify.
- Controls: a different seed (RTA_SEED=alt) on the tip gives a different dump (so the comparison can see a change); the
  urandom trace (count, keys, lengths per sub-batch) is identical across trees; the runner logs which fused kernels each
  run reaches (lincomb2 / _quad_v4 / intt_scaled calls and shapes).

## Code review (git diff 22741456 92dab0ad -- backends/direct/ligero)
- lincomb2 coefficient staging: `c %= P; if (c < 0) c += P;` is exact for every int64 (C++ truncating %, INT64_MIN
  included), then `mont_reduce(c * R64M)` with c, R64M < p gives c 2^32 mod p below 2p, one conditional subtraction: the
  same canonical value as the old `(C % P) * _R32 % P` in torch. The lazy sums of 4 products stay below 2^64 for any
  non-negative int32 X (4 p 2^31 < 2^64), and `canon3p(mont_reduce(.))` is exact for every mont_reduce output (< 2^32 + p
  < 4p). So w and v are exact for any int64 coefficients; X must be non-negative int32, the replaced lincomb_v4 kernel's
  domain too (the prover passes canonical coefs). Adversarial inputs confirm (below).
- beta in `_tests_compute` (0baefa9d): before, the ZK branch bound `_alpha_beta(...)`'s beta to `_beta` and never read it.
  The beta block is pure (torch ops, the cached `_lin_pub_index`), draws no randomness and absorbs nothing into a
  transcript; alpha is computed by the same lines before the new `with_beta` return. The ZK prover's messages are w, h, q,
  v, F; none reads beta. Byte A/B across 0baefa9d confirms it.
- quad_v4: every intermediate canonical; side a scaled by 2^64 / constant by 2^32 so mont(A 2^32 B) = AB; rho scaled by
  2^32. Exact under the same X domain.
- intt_rows: tables built lazily per (n, post.data_ptr()); in the prover the first call is in one of the two eager warm-ups
  `_tests_graph_run` runs on a side stream before capturing, never inside a capture. `intt_ok` needs 4n <= opt-in shared
  memory: n <= 16384 on sm_89 / sm_120 (99 KiB), n <= 32768 on sm_80 (163 KiB) / sm_90 (227 KiB). Larger n falls back to
  field.intt (so the 5090 fp4 config, n = 32768, never reaches intt_rows).
- 92ea2531 / 92dab0ad: scheduling only (slot choice, the warm-up list); no arithmetic. The deterministic runner keys the
  randomness by sub-batch, so a changed number of warm passes cannot mask or fake a difference.
- Robustness regression, not a byte change: quad_v4 stages D * ceil(Q / QUAD_SPLITS=128) * 4 bytes of rho in shared memory
  and lincomb2 stages 2 D chunk 4 bytes (chunk <= 1024 rows), with no opt-in above 48 KiB and no check in `quad_general` /
  `lincomb2_ok`. The launch fails (CUDA_ERROR_INVALID_VALUE, the prover raises instead of falling back) for D = 6 with
  Q > 262144 general constraints per sub-batch, D = 7 with Q > 224768, and lincomb2 at D = 7 (the Fiat-Shamir extension
  degree at 2^-128, protocol.py) when a row chunk exceeds 877 rows (e.g. 40000 rows x 16384 columns). The replaced kernels
  run the same inputs. Reproduced on sm_120 (5090, below). The Table 2 shapes are far from it (see the kernel shapes per target).

## RTX 5090 (sm_120): vy-red-team-arith 5bka200fx8d7jf, SECURE EUR-IS-1, host EPYC 9354, $0.99/h, 23:57Z-00:17Z (~$0.33)
- Bootstrap OK (torch 2.8.0+cu128). Runs r20260925-000238-66aa (bootstrap + tests + A/B), r20260925-000748-f9fc (controls,
  +hash, FS), r20260925-001452-9741 (register). Summaries: evidence/5090/{ab-summary.txt, redteam_arith_test.log, tests_fused_test.log}.
- tests_fused_test.py: bit-exact PASS (all 14 cases).
- redteam_arith_test.py: 225 cases PASS (lincomb2 with int64 extremes, strided C1, every R2 edge, D = 1/2/6/7, prover-sized
  D = 6 up to 40000 x 16384 and D = 7 up to 22730 x 16384; quad_v4 all edge cases; intt_rows n = 2..16384 (32768+ not
  admitted: 99 KiB opt-in); _intt_ginv; reduce_partial; capture). ERROR (launch failure, the robustness regression above):
  lincomb2 D = 7 at 40000 x 16384, quad_v4 D = 6 Q = 300000, quad_v4 D = 7 Q = 250000.
- Byte A/B, fp4-nvf4 l = 8192 p8 (the cell's config, 13 sub-batches, 40 files):
  | config | 22741456 | 9d1a7f15 | 0baefa9d | f550fdc6 | 92ea2531 | 92dab0ad | Rust verify (tip) |
  |---|---|---|---|---|---|---|---|
  | bare interactive | d53a75a5 | = | = | = | = | = | 13/13, 2^-128.11 |
  | + in-proof hash (--auth included-hash) | 354c6d3d | = | = | = | = | = | 13/13, 2^-128.11 |
  | Fiat-Shamir (bare, D = 7) | 3f6f6f0c | . | . | . | . | = | 13/13, 2^-128.40 |
  | control: tip, RTA_SEED=alt | | | | | | c4cb5e88 (differs) | 13/13 |
  (first 16 hex of the sha256 over the per-file sha256 list; "=" identical to base, "." not run.)
- Kernels reached (tip): lincomb2 27 calls (D 6, C1 (6, 1619) row stride 60658, C2 (6, 1583), X (1619, 8448) int32),
  _quad_v4 28 (rho (6, 212), X (1583, 32768)), intt_scaled 0 (n = 32768 > the sm_120 limit: f550fdc6's kernel is not
  exercised on this row; its micro-tests pass up to n = 16384 here).
- Artifacts (all preserved, `data preserved` rc=0 on the pod): evidence tree art:34e47954; dumps bare base art:35fdf2ab,
  tip art:75a715b5; +hash base art:4d2a8176, tip art:25e89894.

## H100 (sm_90): vy-red-team-arith-h100 qhspsqmvfh7wva, SECURE EUR-IS-3, host Xeon 8468, 17-core quota, $3.49/h, 00:18Z-01:16Z (~$3.37)
- The laptop -> pod link ran at ~50-140 KB/s (`pods sync` of the full tree did not finish in 10 min; one attempt also picked
  up another lane's cwd and shipped the wrong tree, which was deleted before use). Shipped instead: `git archive HEAD` of
  the needed subset (3.6 MB: backends/direct, backends/ligero-verify without fixtures, packages/verity/src,
  backends/numerical, tools/research, backends/shared, fixtures/bench-instances, pyproject.toml) at a4333dd0, with
  .research-source.json naming it. Bootstrap OK (torch 2.6.0+cu124, ligero-verify built on the pod, instance caches for
  bf16-hopper(-v3x4), fp8-hopper(-v3x4) at 4096 VUs).
- Runs: r20260925-004904-c8a2 (bootstrap, tests, A/B h8 + h16), r20260925-005745-dac6 (control, +hash, FS),
  r20260925-011026-ec41 (register).
- tests_fused_test.py: bit-exact PASS. redteam_arith_test.py: 227 PASS, including intt_rows at n = 32768 (admitted on sm_90,
  227 KiB opt-in) and `_intt_ginv` at n = 32768; the same 3 launch ERRORs as on the 5090 (quad_v4 56256 B / 54712 B,
  lincomb2 56000 B of shared memory), each with the replaced kernel running the same inputs.
- Byte A/B (local coins; the BF16 cell ran live, the prover's arithmetic is the same):
  | config | 22741456 | 9d1a7f15 | 0baefa9d | f550fdc6 | 92ea2531 | 92dab0ad | Rust verify (tip) |
  |---|---|---|---|---|---|---|---|
  | E4M3 fp8-hopper-v3x4 l=4096 p8 (13 sub-batches) | 1b0e649c | = | = | = | = | = | 13/13, 2^-128.33 |
  | BF16 bf16-hopper-v3x4 l=4096 p8 (25 sub-batches) | f1e0cac4 | = | = | = | = | = | 25/25, 2^-128.05 |
  | E4M3 + in-proof hash: fp8-hopper l=16384 p8 --auth included-hash | 21bce6af | = | = | = | = | = | 13/13, 2^-128.32 |
  | BF16 + in-proof hash: bf16-hopper l=16384 p8 --auth included-hash | 7019296d | = | = | = | = | = | 25/25, 2^-128.05 |
  | Fiat-Shamir: fp8-hopper-v3x4 l=4096 p8 --mode fiat-shamir | 73fa565d | . | . | . | . | = | 13/13, 2^-128.39 |
  | control: E4M3 tip, RTA_SEED=alt | | | | | | 22ed4a03 (differs) | 13/13 |
- Kernels reached (tip, E4M3): lincomb2 27, _quad_v4 28, intt_scaled 56 (f550fdc6's kernel is exercised on sm_90);
  BF16 the same three (27 / 28 / 56).
- Summaries: evidence/h100/{ab-summary.txt, redteam_arith_test.log, tests_fused_test.log}.
- Artifacts (all preserved, `data preserved` rc=0 on the pod, 01:15Z): evidence tree art:6f099c8b; dumps (base / tip)
  E4M3 art:dedd5070 / art:d975bd89, BF16 art:e24484d2 / art:55b40d49, E4M3+hash art:a7af1258 / art:700a7f76,
  BF16+hash art:9e9421a7 / art:edb13e2d. Pod terminated 01:16Z.

## A100 (sm_80): vy-red-team-arith-a100 lqicfeu8nsf6je, SECURE, host Xeon 8470, 24 vCPU, $1.59/h, 01:16Z-01:30Z (~$0.37)
- Same shipped subset (a4333dd0). Config = arith's A100 cell: bf16-ampere-v3 l=16384 p8 on the frozen vu-k1536 set
  (bootstrap BENCH_INSTANCES=1, torch per pod_bootstrap). Runs r20260925-011824-1c9a (bootstrap, tests, A/B, control,
  register), r20260925-012537-0076 (+hash, register). Summaries: evidence/a100/{ab-summary.txt, redteam_arith_test.log, tests_fused_test.log}.
- tests_fused_test.py: bit-exact PASS. redteam_arith_test.py: 227 PASS (intt_rows admitted up to n = 32768 with the
  166912 B opt-in, `_intt_ginv` at 32768), the same 3 shared-memory launch ERRORs, replaced kernels OK on the same inputs.
- Byte A/B (25 sub-batches, 76 files):
  | config | 22741456 | 9d1a7f15 | 0baefa9d | f550fdc6 | 92ea2531 | 92dab0ad | Rust verify (tip) |
  |---|---|---|---|---|---|---|---|
  | BF16 bf16-ampere-v3 l=16384 p8 | 42919dbd | = | = | = | = | = | 25/25, 2^-128.05 |
  | BF16 + in-proof hash: bf16-ampere l=16384 p8 --auth included-hash | ad428dbc | . | . | . | . | = | 25/25, 2^-128.05 |
  | control: tip, RTA_SEED=red-team-arith/control | | | | | | e6d76b4e (differs) | 25/25 |
  `--auth included-hash` on bf16-ampere-v3 itself raises in `hashchain._private_operands` ("operand pins ... differ from the
  expected decode triples") on the base tree and the tip alike (a pre-existing relation limit, not arith's), so the hash
  row uses the committed bf16-ampere relation, as the H100 hash rows use bf16-hopper.
- Kernels reached (tip): lincomb2 27 (D 6, C1 (6, 1665) row stride 118791, X (1665, 16640) int32), _quad_v4 28
  (rho (6, 881), X (1629, 65536)), intt_scaled 0 (n = 65536 > the sm_80 limit of 32768: f550fdc6 falls back on this row).
- Artifacts (all preserved, `data preserved` rc=0 on the pod): evidence trees art:d30a7b45 (bare/control) and art:6f8e4c5c
  (final, incl. +hash); dumps bare base art:3f4336b3, tip art:65003df1; +hash base art:d85ac42b, tip art:080e5498
  (art:abe5e3e7 / art:a93406b1 hold only the logs of the failed bf16-ampere-v3 + hash attempt). Pod terminated 01:30Z.

## Verdict (per commit x target; "PASS" = proof bytes identical to base 22741456 under fixed coins, Rust verifier accepts)
| commit | RTX 5090 sm_120 (fp4-nvf4) | H100 sm_90 (E4M3, BF16) | A100 sm_80 (BF16) |
|---|---|---|---|
| 9d1a7f15 quad_v4 + reduce_partial | PASS | PASS | PASS |
| 0baefa9d lincomb2_v4, beta dropped | PASS | PASS | PASS |
| f550fdc6 intt_rows | PASS (kernel not reached, n=32768) | PASS (reached, 56 calls) | PASS (kernel not reached, n=65536) |
| 92ea2531 / 92dab0ad scheduling + warm | PASS | PASS | PASS |
Bare rows all 6 trees; +hash rows all 6 trees on 5090/H100, base vs tip on A100; FS base vs tip on 5090/H100.
No counterexample to byte equality. Separate robustness finding (a crash, never a different byte): quad_v4 / lincomb2
launch fail above 48 KiB of dynamic shared memory (D=6 Q>262144, D=7 Q>224768, lincomb2 D=7 chunk>877 rows), where the
replaced kernels run; Table 2 shapes are 4-10x below those limits. 4090 (sm_89) not run: its opt-in limit and code
paths are those of the 5090.

## FINAL
~~~text
tip: lane/red-team-arith @ a4333dd0 (base lane/arith@92dab0ad)        merge-with: none (test-only files; optional)
known-failures: none (redteam_arith_test "FAIL" = the 3 smem launch ERRORs below)    pod: terminated 01:30Z; $4.07
artifacts: art:34e47954 art:35fdf2ab art:75a715b5 art:4d2a8176 art:25e89894 art:6f099c8b art:dedd5070 art:d975bd89 art:e24484d2 art:55b40d49 art:a7af1258 art:700a7f76 art:9e9421a7 art:edb13e2d art:d30a7b45 art:6f8e4c5c art:3f4336b3 art:65003df1 art:d85ac42b art:080e5498 art:abe5e3e7 art:a93406b1
~~~
red-team arith: PASS. Every commit (9d1a7f15, 0baefa9d, f550fdc6, 92ea2531/92dab0ad) leaves the proof bytes identical to
main 22741456 under fixed coins on RTX 5090 (sm_120), H100 (sm_90) and A100 (sm_80): bare, + in-proof hash, and FS (5090,
H100); Rust verify accepts every tip dump at 2^-128; a changed seed changes the dump on each target. No counterexample.
- Robustness finding for arith (a crash, never a different byte): quad_v4 / lincomb2 launch without the >48 KiB shared
  memory opt-in (D=6 Q>262144, D=7 Q>224768, lincomb2 D=7 chunk>877 rows); fix by opting in or gating the fused path.
- f550fdc6's intt_rows is reached only on the H100 row (n=32768); on the 5090 (n=32768) and A100 (n=65536) the Table 2
  cells fall back, so there it is covered by micro-tests only (n <= 16384 / 32768).
- Handoffs sent: lanes/coordinator/20260925T0135Z-handoff-from-red-team-arith.md, lanes/arith/20260925T0135Z-handoff-from-red-team-arith.md.
  kb: pipelined-bench-timing.md "Fused prover kernels: byte equality and shared-memory limits".
- Pods: vy-red-team-arith (5090) ~$0.33, vy-red-team-arith-h100 ~$3.37, vy-red-team-arith-a100 ~$0.37; all terminated.
