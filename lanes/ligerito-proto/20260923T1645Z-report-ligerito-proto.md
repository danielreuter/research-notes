---
lane: ligerito-proto
kind: report
created: 2026-09-23T16:45Z
status: final
---

FINAL 7bc2fdd (20:35Z) — see `## FINAL` below. Pod 84jhmc4tfh8w9n terminated 20:17Z (17:22Z–20:17Z, 2.9 h × $0.74 = $2.15 of the $4).

CHECKPOINT 7bc2fdd (20:20Z) — all measurements done (q=192 sweep 2^26/28/29 + 2^30 OOM; paper-style ℓ=3/ℓ=4 |S|=148 at 2^29;
ligerito-design's pow2 F point at 2^29 AND 2^30, S point at 2^29); six `bench-result/v1` artifacts in the store (ids in `## FINAL`);
pod terminated. Laptop torch was uninstalled by the coordinator (17:30Z rule) — all torch tests/benches ran on the pod (14 tests green).

CHECKPOINT b4d7e12 (17:45Z) — the whole PCS is written and green: 12 tests (ext field axioms, x^6−31 irreducible, tensor
claims, column sumcheck round trip, prove/verify at n = 9/10/12 with 1–3 committed rounds, bytes round trip, 8 negatives, dims
constraints, GPU encoder bit-exact vs `field.ntt` for R = 2^8..2^15, GPU contraction kernels vs torch) pass on the laptop (CPU
fallbacks) AND on the pod. Pod `vy-ligerito-proto` = 84jhmc4tfh8w9n, RTX 4090 24564 MiB **reference part** (EPYC 7352 host,
EU-RO-1, $0.74/h, created 17:22Z, watchdog 4.6 h armed, `[machines.vy-ligerito-proto]` in machines.toml), bootstrapped venv312
torch 2.6.0+cu124 + cupy-cuda12x + blake3 (17:10 pod clock). Read §9 17:00Z (Phase B today; I own `transcript.py`; H100 allowed
if 2^30 OOMs) and wave-b brief §1 (module ownership). `ligerito-design/` has no note yet. Next: `proto/bench.py` (per-N
buckets + encoder baseline + negatives → bench-result JSON), first GPU numbers at 2^26.

## Interface (frozen 17:45Z) — `backends/direct/ligerito/transcript.py` (Coins protocol; every Ligerito lane draws randomness ONLY here)

~~~
coins.absorb(label: bytes, data: bytes) -> None       prover message (root, sumcheck message (3,6), opened rows, siblings, y)
coins.challenge(label: bytes, n: int) -> np.ndarray   (n, 6) int64 F_{p^6} elements, coords in [0, p); ONE coin (round trip)
coins.indices(label: bytes, domain: int, count: int) -> list[int]   count DISTINCT positions in [0, domain); one coin
coins.rounds -> int                                   sequential verifier messages so far
~~~
Impls in the file: `FiatShamirCoins` (BLAKE2b chain + SHAKE-256 squeeze; the prototype), `LocalCoins(seed)` (deterministic,
ignores absorbs — diagnostic only), `LiveCoins(slots)` (one 32-byte verifier coin per round trip from `live.py`'s slot stream;
SHAKE-256 of the coin for that round's draw; 8c: challenges are functions of verifier coins alone; surface fixed, not exercised by
the prototype). Call order IS the protocol: per committed round i: absorb root_i → (k'_i ×: absorb g (3,6), challenge 1) →
[i ≥ 2: indices(S_{i−1}) after absorbing the opened rows + siblings, then challenge(1 + |S_{i−1}|) = α batching coefficients] →
final: absorb y_L, indices(S_L). Rounds = Σ_i (1 + k'_i + 1) + 1 ≈ n − k_L + 2ℓ + 1 (e.g. n = 29, ℓ = 3, k_L = 15: 21 coins).
Extension: F_{p^6} = F_p[x]/(x^6 − 31), coordinate i = coefficient of x^i, 24 B/element (`proto/ext.py`; numpy + torch planes).
NOTE for ligerito-design / -sumcheck: Ligero's `protocol.py` "extension" is D independent BabyBear coordinates (a product ring,
fine for its linear tests) — the sumcheck needs a FIELD (inversion-free here, but the soundness argument needs |F| = p^6), so it
cannot be reused; `proto/ext.py` is the field. Top-level `pcs.py`: `prove(f (N,) int32 device, z (n,6), dims, coins=...) ->
Proof`, `verify(proof, z, v) -> (bool, reason)`; commit is fused into round 1 (`proof.roots[0]` is the commitment).

CHECKPOINT none (16:55Z) — brief, paper, PROTOCOL.md, encode_simt/merkle/field/encoder_bench read; worktree `~/projects/verity-main-wt/ligerito-proto` on `lane/ligerito-proto` from e0cf2cd; design fixed (below); no pod yet (code first, pod when the GPU path is ready to test).

# ligerito-proto — Ligerito PCS (commit + eval proof + verify) over BabyBear^6 on a 4090 at N = 2^26 .. 2^30

## 0. Design decisions (fixed 16:55Z; `## For ligerito-design` lists what they should confirm)

* Field: BabyBear p = 2^31 − 2^27 + 1; challenges in F_{p^6} = F_p[x]/(x^6 − 31) (31 = the multiplicative generator is
  neither a square nor a cube, so x^6 − 31 is irreducible: 6 | p − 1). Ext element = 6 base coords, 24 B.
* Code: coefficient-basis Reed–Solomon, rate 1/4, evaluation domain the subgroup <w_n> (n = 4 · 2^k), NO INTT (the
  message IS the coefficient vector). Generator row s = (η_s^x)_x = ⊗_j (1, η_s^{2^j}) — tensorizable, so every
  verifier-side "opened row" claim is a tensor claim like the evaluation claim itself.
* Layout: the polynomial f (N = 2^n base coefficients, flat) IS the column-major matrix M̃_1 (R_1 = 2^{k_1} rows ×
  C_1 = 2^{k'_1} columns: x = row + R_1 · col). Encoding is along the TALL axis (each column → 4 R_1 symbols); the
  Merkle tree is over the 4 R_1 codeword rows (leaf s = Blake3 of the C values at index s). In memory the codeword is
  U (C, 4R) row-major, so the leaf hashing is exactly `backends/shared/hash_gpu/merkle.commit` (one leaf per column
  of a (rows, N) buffer, coalesced) and the message needs no transpose.
* Big NTT (4 R_1 = 2^24 at N = 2^29): 4-step Cooley–Tukey n = n1 · n2 (n1, n2 ≤ 4096) with a cupy RawKernel that
  transforms a (B, n, inner) tensor along its middle axis in shared memory (radix-2 DIT, Montgomery twiddles from
  `encode_simt`'s table helpers), G adjacent inner columns per CTA for coalescing; step A over n2 with the zero-pad
  (only n2/4 inputs) and the ω^{j1 k'} twiddle fused into the store; step B over n1 in place. Codeword position
  s = k' · n1 + k1 holds P(ω^{k' + n2 k1}).
* Rounds (paper §6): round i commits M̃_i; the opened rows S_{i−1} of the previous codeword become |S| tensor claims
  ⟨(η_s^x)_x, y_{i−1}⟩ = ⟨U_{i−1}[s, :], r̄_{i−1}⟩ on y_{i−1} = vec(M̃_i); batched with the running claim by α; the
  partial sumcheck over the k'_i COLUMN variables (the high bits) is done as: u_t = M̃_i^T rowpart_t for every claim
  term t (round 1: one term, a fused int32 kernel; rounds ≥ 2: fp64 16-bit-limb matmuls, exact), then a tiny
  sumcheck on the (T × C_i) table on the host, then y_i = M̃_i r̄_i (round 1: kernel; later: limb matmul). The batched
  claim vector is a LIST of tensor terms (1 eq term + Σ_{j<i} |S_j| geometric terms); nothing of size 2^n is ever
  materialised in the extension.
* Round 1 stays in the base field (f is base); y_1 and everything after are in F_{p^6}; later matrices are committed
  as 6 base coordinate planes (RS encoding is F_p-linear), so an opened row of round i ≥ 2 is C_i ext = 6 C_i base words.
* Queries: |S| = 192 per round by default ((5/8)^192 = 2^-130.2 per round; union over 3 committed rounds + tail
  2^-128.6; field terms ~2^-180). Dimensions from the paper's Appendix A optimizer (c_1 = |S|·4 B, c_i = |S|·24 B,
  c_ℓ = 24 B) with the power-of-two rounding. Overridable from the CLI when ligerito-design's numbers land.
* Coins: Fiat–Shamir (BLAKE2b transcript) for the prototype; the round structure is interactive-friendly and the
  sequential coin count is reported (Σ_i (|S| set + α + k'_i) ≈ 2ℓ + n − k_{ℓ−1}).
* Not in scope here: ZK, the relation/zero-check, Rust verifier.

## For ligerito-design
* Extension: F_p[x]/(x^6 − 31); coefficient-basis RS on <w_n>; tensor claim representation as above. If your ref.py
  differs (irreducible, basis, domain), tell me in your note — the verifier here is parametrised by (β, domain).
* I default to |S| = 192 every round and the Appendix-A dims; post your (ℓ, k_i, k'_i, |S_i|) and I re-run.

## FINAL (20:35Z) — Ligerito PCS prototype measured on the 4090 at N = 2^26 … 2^30

Code: `backends/direct/ligerito/{pcs.py,transcript.py}` (public surface) + `backends/direct/ligerito/proto/` (`ext.py` F_{p^6},
`dims.py`, `claims.py` tensor claims + column sumcheck, `ntt_gpu.py` tall-axis 4-step NTT, `kernels.py` round-1 contractions,
`linalg.py` exact fp64-limb GEMMs + ext planes, `merkle_multi.py` batched multi-opening, `pcs.py` prover/verifier, `bench.py`,
`pcs_test.py` 14 tests). Branch `lane/ligerito-proto` head **7bc2fdd** (from e0cf2cd; 4 commits; `git status --short` empty; nothing
under `backends/direct/ligero/` touched; no .md added to the repo). Numbers below are medians of 3 reps (2 at 2^30), each after an
untimed warm run at the same shape (kernel compiles excluded); Fiat–Shamir coins; verifier = numpy on the pod's EPYC host, 1 thread.

### Table A — my default parameters (|S| = 192 every round, rate 1/4, Appendix-A dims capped at codeword 2^24) vs today's encode+commit

| N (cells) | rounds (M̃_i = rows × cols) | prover wall | = commit | + recursion+sumcheck | + serialization | proof | verify | peak mem | TODAY encode+commit same cells (`encode_simt` 4096-wide + fused BLAKE3 Merkle) | ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| 2^26 | 2^19×2^7, 2^15×2^4, 2^11×2^4; final 2^11 | **0.142 s** | 0.008 | 0.122 | 0.010 | **454 KB** | 0.063 s | 1.9 GiB | 0.0044 s (enc 0.0025 + commit 0.0019) | 32× |
| 2^28 | 2^22×2^6, 2^18×2^4, 2^14×2^4, 2^10×2^4; final 2^10 | **0.331 s** | 0.048 | 0.267 | 0.015 | **532 KB** | 0.060 s | 10.5 GiB | 0.017 s (0.010 + 0.007) | 19× |
| 2^29 | 2^22×2^7, 2^18×2^4, 2^14×2^4, 2^10×2^4; final 2^10 | **0.372 s** | 0.088 | 0.269 | 0.015 | **581 KB** | 0.060 s | 18.5 GiB | 0.034 s (0.019 + 0.014) | 11× |
| 2^30 | 2^22×2^8 … | OOM on 24 GiB: f 4 GiB + round-1 codeword 16 GiB + tree ~1 GiB | | | | | | >23.5 GiB | 0.068 s (0.038 + 0.029) | — |

Bucket detail at 2^29 (s): sumcheck_host 0.128 · recursion_contract 0.097 · commit_r1_encode 0.062 · commit_r1_merkle 0.025 ·
sumcheck_r1_contract 0.021 · recursion_fold 0.019 · serialize_openings 0.013 · everything else < 0.005. Coins (sequential verifier
messages): 20 / 25 / 26. Predicted bytes (no path dedup) 609 / 739 / 788 KB → measured 454 / 532 / 581 KB (the batched multi-path
saves ~25 %). Negatives at EVERY N: wrong evaluation, tampered opened row (round 1), tampered opened row (last round), wrong final
vector, tampered sumcheck message — all rejected (plus tampered root and a proof for another polynomial in the unit tests).

### Table B — ligerito-design's D1 pow2 parameter points (their note 17:55Z), run unchanged (per-round rates and |S| now supported)

| point | N | rounds (rate, |S|) | prover | commit / rec+sc / serial | proof (predicted) | verify | peak | today enc+commit |
|---|---|---|---|---|---|---|---|---|
| **F** | 2^29 | 2^22×2^7 (1/2, 311), 2^17×2^5 (1/4, 191), 2^12×2^5 (1/4, 193); final 2^12 | **0.355 s** | 0.043 / 0.298 / 0.013 | **790 KB** (985) | 0.124 s | 10.2 GiB | 0.034 s |
| **F** | **2^30** | 2^23×2^7 (1/2, 311), 2^18×2^5, 2^13×2^5; final 2^13 | **0.525 s** | 0.090 / 0.419 / 0.015 | **911 KB** (1106) | 0.316 s | 20.3 GiB | 0.068 s |
| **S** | 2^29 | 2^23×2^6 (1/4, 191), 2^19×2^4 (1/16, 143), 2^15×2^4, 2^12×2^3, 2^9×2^3 (1/16, 143/144); final 2^9 | **0.524 s** | 0.092 / 0.412 / 0.018 | **508 KB** (706) | 0.060 s | 22.6 GiB | 0.034 s |
| paper-style ℓ=3 | 2^29 | 2^20×2^9, 2^14×2^6 (1/4, 148); final 2^14 | 0.192 s | 0.076 / 0.093 / 0.009 | 1.03 MB | 0.177 s | 10.8 GiB | (|S|=148 at rate 1/4 is only 2^-100/round) |
| paper-style ℓ=4 | 2^29 | 2^22×2^7, 2^17×2^5, 2^12×2^5 (1/4, 148); final 2^12 | 0.293 s | 0.090 / 0.191 / 0.011 | 558 KB | 0.072 s | 13.5 GiB | (same caveat) |

The S point at 2^30 (codeword 2^26 × 64 columns = 16 GiB) does not fit the 4090 with f resident — exactly ligerito-design's warning;
their streaming-leaf + recompute-openings idea (or an 80 GB H100) is the fix, not built here.

### The answer to the brief's question

At our N (2^29.4 ≈ between the 2^29 and 2^30 rows): **no, not yet — measured 0.37–0.53 s for the PCS ALONE**, against today's whole
fp8-ada 4090 prover of 0.252 s live / 0.17 s local-coin (which includes encode, commit, all three tests, device witness and 66 MB of
serialization), and against 0.034–0.068 s for today's encode+commit of the same cells. So the prototype is 1.5–3× today's full prover
and 10–20× today's encode+commit, and it does not yet include the zero-check sumcheck over N cells (ligerito-sumcheck's module).
**Proof bytes are the win and they are real: 0.51–0.91 MB per 2^29–2^30 cells (113–130× smaller than today's 66 MB), measured,
with the verifier accepting and every tamper rejected.** ligerito-design's predicted-bytes model over-predicts by 20–30 % (multi-path
dedup) — their table's S/F bytes are conservative.

Where the time goes (2^29, default params; the same three items dominate every configuration):

1. **Host-side sumcheck bookkeeping, 0.13–0.15 s (35–40 %)**: `ColumnSumcheckProver` runs the k'_i column rounds on a (T × C_i × 6)
   numpy table with T = 1 + Σ|S_j| ≈ 200–600 tensor terms — ext × ext products (36 base mults) as numpy tensordots, ~500 small
   numpy calls per proof (was 1.6 s before vectorising; the residual is Python/numpy call overhead, not arithmetic). It is O(T · C_i)
   work — microseconds on the GPU. Fix: one small CUDA kernel (or torch on-device) for round_message/fold, and compute the |S| row
   claims + α batching on the device. Expected → < 10 ms.
2. **Recursion contractions u_t = M̃_i^T · η_t^{row}, 0.10–0.17 s (25–35 %)**: exact modular GEMMs done as fp64 16-bit-limb products
   (3 GEMMs of (6C_i × R_i) × (R_i × T)) — the RTX 4090 has 1.3 TFLOPS of fp64, so 1.4e10 MACs at 2^29 is ≥ 22 ms of pure GEMM plus
   limb conversion passes. Fix: int8 tensor cores (`torch._int_mm`, 4 limbs, K-chunks of 2^15 — 660 TOPS on the 4090) or, better,
   note that u_t[c] = P_c(η_t) is an RS evaluation of column c: for the |S| points of ONE previous codeword domain it is a partial
   NTT (η_t ∈ <w_{4R_{i−1}}>) — a "sparse-output NTT" kernel makes it O(R_i log) per column instead of O(R_i · T). Expected → ~10 ms.
3. **Round-1 encode, 0.06 s at 2^29 (17 %)**: my tall-axis 4-step NTT (two shared-memory passes, 52 B/cell of traffic, 440 GB/s
   nominal) is 3.3× slower than `encode_simt`'s fused single-pass row NTT (19 ms for the same cells, 20 B/cell). The transposed path
   is not directly usable (encode_simt is specialised to l ≤ 16384; the tall axis is 2^22–2^24), so the fix is a fused 4-step with
   the n1-transpose done on-chip (or `encode_simt`'s kernel generalised to the 4-step's inner transforms). Expected → 20–25 ms.
   BLAKE3 Merkle is already the shared `hash_gpu` kernel: 25 ms for 2^24 leaves of 512 B (same as Ligero's per byte).
4. Smaller: recursion_fold y = M̃ r̄ as fp64 GEMM 0.02 s (→ kernel); serialize_openings 0.013 s (device gather is fine; the
   `merkle_multi.plan` is Python); round-1 col_contract 0.02 s is at 300 GB/s (fine).

Bottom line: the PCS's GPU-inherent work at 2^29 is encode 20–60 ms + Merkle 25 ms + contractions ~10–20 ms + folds ~5 ms ≈
**0.06–0.11 s** once items 1–3 are engineered; add ligerito-sumcheck's degree-3 zero-check pass (one read of N cells in the extension
per variable-halving — my estimate 30–60 ms on 1 TB/s) → ~0.1–0.17 s PCS+sumcheck, i.e. ≤ 1.3 × today's 0.17 s local-coin prover is
PLAUSIBLE but UNMEASURED; the measured prototype is 2.2–3× it. The 4090 memory ceiling (S point at 2^30 = 20 GiB codeword) is the
other hard constraint at our batch size.

### What was reused from the Ligero code (nothing under `ligero/` edited)
* `backends/shared/hash_gpu` BLAKE3 Merkle via `ligero/merkle.py`'s `_gpu_merkle.commit` / `digest_bytes` (leaf = one codeword row
  = one column of the (W, n) buffer — my layout was chosen so this is a zero-copy fit); the device tree `levels[k]` for the gathers.
* `ligero/encode_simt.py`'s `_mont`, `_powers` (Montgomery twiddle tables) and its Montgomery butterfly idiom in my kernel;
  `ligero/field.py`'s `P`, `root_of_unity`, `ntt` (CPU fallback + the bit-exactness reference for the GPU encoder).
* `encode_simt.encoder_for` + `merkle.commit_device` as the "today" baseline in `bench.py` (measured, not quoted).
* NOT reusable: `protocol.py`'s "extension" is D independent BabyBear coordinates (a product ring) — Ligerito's sumcheck needs the
  field F_{p^6}; wrote `proto/ext.py`.

### Artifacts (`research data put`, kind bench-result/v1, labels `--by ligerito-proto`; local store — `research data push` needs
AWS credentials my shell does not have, so the coordinator's `push --pending` is required)
* `art:d08ec12c…` q192 sweep 2^26/2^28/2^29 (+2^30 OOM record) — Table A
* `art:664bf2e6…` design F @ 2^29 · `art:7f4de241…` design F @ 2^30 · `art:dcb89b9d…` design S @ 2^29 — Table B
* `art:726c2501…` ℓ=3 |S|=148 @ 2^29 · `art:63137593…` ℓ=4 |S|=148 @ 2^29
Full ids: d08ec12c838ce6e176d56c0792922f5223210e7f93585e32947d9e03c3106852, 664bf2e610d77ee531f86b0ec67391bcab6258e64497cb58578f5ad6ab8a1b3d,
7f4de24186f8af989cd3fbe039b70f57326008e7221b2f86a7ea92eb1d6d0523, dcb89b9db88674dc10a658567ffcfc95506f2c89f99a8da10441c13a206d2bef,
726c2501eb8a8d0e0c2898610f1ca0bcb1aa1e6f54e858332ff7b5fdd62264b9, 6313759390d2b5b5c73ab8c201f67d221e3c132ff0204637757f97655f849f6d.

### Ranked list — what Phase B must solve
1. **Move the recursion bookkeeping off the host** (item 1 above): device-side row claims, α batching, column sumcheck rounds. Biggest
   single win (−0.13 s), pure engineering; also removes ~20 host↔device syncs per proof (matters for the live-coin round trips).
2. **Contractions without fp64**: sparse-output NTT for the geometric terms (or int8 tensor-core limb GEMM). −0.1 s at 2^29; on an
   H100 fp64 is 60 TFLOPS so the pain is Ada/Blackwell-consumer specific — decide per target device.
3. **Round-1 encoder**: fused 4-step (on-chip transpose) to reach `encode_simt`'s 20 B/cell; and the **streaming commit** (hash leaves
   out of the NTT, recompute the |S_1| opened rows as a (C_1 × R_1) × (R_1 × |S_1|) base GEMM) so the 2^26-length S-point codeword
   (16–34 GiB) never lives in memory — mandatory for S at 2^30 on 24 GiB and for bf16's 2^27.
4. **The zero-check sumcheck over N cells in F_{p^6}** (ligerito-sumcheck): not in this prototype; it is the one remaining O(N)
   extension-field pass and its eval claims feed `prove`; measure it before believing the ≤ 1.3× projection.
5. **Verifier**: 60–320 ms numpy is fine for a prototype; the Rust verifier (ligerito-verify-rs) should reproduce
   `merkle_multi.plan` (batched multi-path, ~25 % of the bytes) and the tensor-claim final check — both are specified in code here.
6. **Soundness accounting**: the prototype's |S| = 192/rate 1/4 is unique-decoding 2^-130/round; ligerito-design's allocation (172/140
   with 1/16 later rates) is what to ship; list-decoding (|S| ≈ 90) is the −200 KB lever they flagged.
7. **Live coins**: `LiveCoins` surface exists; the protocol needs 22–29 sequential coins at 2^29–2^30 (vs today's handful) — live-2's
   round-latency numbers decide whether c = 2 variables per coin (ligerito-design) is needed.
