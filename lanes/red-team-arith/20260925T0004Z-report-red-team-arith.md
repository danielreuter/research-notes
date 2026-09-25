---
lane: red-team-arith
kind: report
created: 2026-09-25T00:04Z
status: open
---

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
