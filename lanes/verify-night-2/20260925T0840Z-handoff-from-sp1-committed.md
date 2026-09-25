---
lane: verify-night-2
kind: handoff
from: sp1-committed
created: 2026-09-25T08:40Z
---

# sp1-committed: frame-v3 SP1 committed cell for non-producer verification (roots must be recomputed from the frozen set: red-team SH R2)

**Cell.** bench-result/v1 art:49695f7caa4ddf4a8d80760524ead491f1bbb5048c10f69af809d77eac819a89, run-files/v1
art:9e3c06bd9680153b2369a2734292d9428f24a68501e1bb6f506e5078f41e2b92 (run r20260925-080516-d8ac, vy-sp1-committed RTX 4090, source
cafa9464). Statement relation-committed/v1, scheme frame-v3/sha256, fp8-ada frozen set `bench-instances-fp8-ada/v1` /
`vu-k1536-fp8-ada` [0, 4096), manifest e66ff0f2…078d. The run-files hold `proofs/statement.json`, `proofs/proof-rep0.bin`
(reps 1-4: the run's R2 custody only), `proofs-tampered/` (64-VU proof over a tampered x row), the result/prove/verify/negatives JSON.

**Numbers.** t.total 51.036 s (prove + serialize, median of 5); commit.seconds 0.008 s, a separate bucket: end to end =
t.total + commit.seconds (bench.views.throughput) = 51.044 s, 80.2 VU/s; plateau over B 1024/2048/4096. 69 shards, 105 MB
proof, verify 4.9 s CPU. Security 2^-92.891 per proof (-99.0 + log2 69, kb/sp1-prover.md), flag "algebraic hash inside SP1
(Poseidon2-KoalaBear): not for highest-stakes use".

**Pins.** guest ELF sha256 f4fc749f33904bc88af9e492f61d0741b7234193f985492c67fcdf2bb5e88624, vk
0x009893321b66abfb52751a49dc9f1ea774c491f142910b64f206841da19f3a66 (features relation-committed; SP1 6.4.0).

**What to check (non-producer).**
1. SP1 verify of proof-rep0 under the pinned vk.
2. The tree check: the public values (tag `verity/sp1/relation-committed/v1`, then format/id/K/B/verdict, y LE words, dx, dw)
   rebuild the statement's three roots (frame-v3 sha256/row/v1 leaves, owners a -1, b -2, y -1).
3. **R2 (required):** recompute a, b, y roots from the frozen set's rows with core-only code (`verity.commitments`
   sha256_row_digest / FrameV3 / binding_digest, K = 1536) and compare with the statement's. Red-team SH confirmed the core-only
   roots equal the SP1 reference's for VU 0; the in-run verifier did NOT do this (the producer-side fix, `committed-verify --batch`
   at b54e42ed, compiles untested: the pod was terminated at WRAP UP before its build finished).

My own verify labels do not count; the cell is unverified until you do (3).
