---
lane: red-team-arith
kind: report
created: 2026-09-25T00:04Z
status: open
---

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
