---
lane: ligerito-design
kind: report
created: 2026-09-23T16:45Z
status: open
---

FINAL 760260d (18:25Z) — see `## FINAL` at the end.  All three deliverables landed before their (moved) deadlines; `lane/ligerito-proto`
7bc2fdd merged in as §9 18:20Z asked (`__init__.py` docstring merged, nothing else overlapped); 42 laptop tests (numpy only, 20 s);
`git status --short` empty.

CHECKPOINT 760260d (18:22Z) — read §9 18:20Z (proto FINAL, ownership change to ligerito-pcs-fast, "base on 7bc2fdd"): merged 7bc2fdd
(commit 2d6ad3a); ref.py verified to run unchanged on proto's `transcript.FiatShamirCoins` / `LocalCoins` (new interop test);
`params.py` byte model checked against proto's EIGHT measured proofs — within 1 % once the paper's "expected symbols" are not counted
(proto/ref.py let the verifier compute them; `send_expected_symbols=False` is now the default and the table numbers dropped ~14 KiB);
the prover model gained proto's `recursion_contract` bucket (carried RS-row claims contracted against M_i, 2e10 base-eq for B).  On
proto's measured 0.37 s at 2^29: the model's encode (0.054 s vs 0.062 measured) and Merkle (0.030 vs 0.025) buckets are right; the
0.24 s gap is their host-side sumcheck (0.128) + fp64-limb contractions (0.097) — engineering, now ligerito-pcs-fast's items 1–3; the
model's on-device figure for the same work is 0.024 s.

CHECKPOINT 9323f4e (18:10Z) — D2 done ahead of 20:30Z: `backends/direct/ligerito/ref.py` (+ `test_ref.py`, 19 tests, 3 s) — the
numpy reference PCS over BabyBear / F_p[x]/(x^6-31): commit / prove_eval / verify at 1–3 levels, binary and radix-3 (3 x 2^k tall)
shapes, coefficient-basis RS on <w_n> in natural order, batched BLAKE3 Merkle multi-openings, a Fiat-Shamir `FSCoins` with the proto's
`absorb / challenge / indices / rounds` signature, JSON fixtures (`python -m backends.direct.ligerito.ref` prints 4 statement+proof+verdict
fixtures, 155 KB) for ligerito-verify-rs.  Negatives: wrong value, wrong commitment / point, witness changed after commit (both ways:
honest rows -> claim mismatch; own rows -> Merkle), tampered opened symbol / sibling, tampered sumcheck coefficient, tampered final
vector, inconsistent fold between levels ("wrong symbol"), wrong query set.  `params.py` now also reports a *balanced* point (below);
34 tests total, 27 s.  Next: D3 design note (§3–§8 below) by 22:00Z.  `git status --short` empty.

CHECKPOINT 00b6353 (17:55Z) — D1 done: `backends/direct/ligerito/params.py` (+ `test_params.py`, 14 tests, 45 s CPU) reproduces the
paper's Table 1 at 148/243/356/418 KiB vs 145/255/360/420 (x1.02/0.95/0.99/1.00; the optimizer lands exactly on the docs.rs
crate's 2^20 config: 2^14x2^6 base level, 2^10x2^4 ext level, final 2^10) and gives our five Table 2 cells (below). Worktree
`~/projects/verity-main-wt/ligerito-design`, branch `lane/ligerito-design` from e0cf2cd. Read §9 through 17:30Z (Phase B today;
deadlines 18:15 / 20:30 / 22:00Z; no torch on the laptop — this lane is numpy-only anyway; `df` 11 GB free). Read the proto note
(17:45Z interface): my ref.py will use THEIR conventions (F_p[x]/(x^6-31), coefficient-basis RS on <w_n>, column-major layout,
Coins protocol signature) so the Rust verifier fixtures match. Next: ref.py by 20:30Z.

# ligerito-design — Ligerito for the Verity relation IR: parameters, reference PCS, design

## 1. D1 — the calculator (`params.py`)

Model (all formulas are in the module docstring and in every returned dict under `formula`):

* Level `i = 1..L` commits `M_i` (`tall_i x wide_i = 2^{k'_i}`), every column RS-encoded along the TALL axis to length `n_i = 2^m`
  (coefficient basis, no INTT; `rate_i = tall_i / n_i`); Merkle over the `n_i` codeword rows (BLAKE3, 32 B). Partial sumcheck over the
  `k'_i` wide variables → `v_i = M_i r_i` reshaped into `M_{i+1}`; the verifier opens `|S_i|` rows and the prover sends the expected
  symbols `y_i = (G_i v_i)_{S_i}` whose check is batched into level `i+1`'s sumcheck. `v_L` (`final_len` ext elements) is sent in the clear.
* Bytes (paper (19)): `Σ_i (|S_i| wide_i elem_i + E[siblings](n_i,|S_i|)·32 [+ |S_i|·32 salt if ZK] + (|S_i|+1)·24 + 3k'_i·24) + final_len·24
  + L·32 + relation messages`; `elem_1 = 4 B` (base), `elem_{i>=2} = 24 B`. `E[siblings]` is the exact expectation for a batched
  multi-opening (`Σ_depth Σ_nodes P(node occupied ∧ sibling empty)`, hypergeometric; Monte-Carlo-checked in the tests) — it is what
  makes 2^20 come out at 148 not 234 KiB.
* Soundness (paper (17), unique decoding, `e_i = (n_i - tall_i)/2`): per level `((1+rate_i)/2)^{|S_i|} + k'_i n_i/|F| + 2k'_i/|F| +
  (|S_{i-1}|+1)/|F|`, `|F| = p^6 = 2^185.4`; plus the relation terms (zero-check: `(Q+Lin)/|F|` batching, `col_vars/|F|` eq(tau),
  `(3 col_vars+11)/|F|` sumcheck; (i,i') sumcheck `4 row_vars/|F|`; claim batching). Every field term is < 2^-150; the query terms are
  sized so the UNION is ≤ 2^-128 (`allocate_queries`: equal split then greedy re-allocation by bytes-per-query).
* Coins: `1 + zero-check rounds + (i,i') rounds + Σ_i ceil(k'_i/c) + 2(L-1) + 1` with `c = 2` sumcheck variables per coin (degree-3
  messages cost 4^c ext elements each; c = 2 halves the round count for +12 B/round).
* Prover op model in base-multiply equivalents (ext x base = 6, ext x ext = 36; BLAKE3 in bytes; NTT in butterflies) with the same
  units applied to today's B-Ligero (PROTOCOL.md §4/§8, `ligero_today_ops`), and a GPU throughput table (NOT measurements:
  butterflies 0.5–0.7 T/s from enc-hopper's barrier-bound number, 5–8 T base mults/s, 300–500 GB/s BLAKE3) for time estimates.

Layout for our batches: witness `rows_pad x cols` with `rows_pad = 4096` (3769 real rows for fp8-ada + ZK mask rows) and
`cols = 3 x 2^16` (fp8-ada; `K = 1536 = 3 x 512` units per VU) or `3 x 2^17` (bf16) — the factor 3 stays in the TALL dimension of every
level (`tall_i = 3 x 2^j`; the RS length is the next power of two so the *effective* rate is `3/16` at nominal 1/4, `3/8` at nominal 1/2) and
costs one ternary sumcheck variable; the alternative (`radix3=False`) pads the columns to `2^18` (+33 % cells, 583 KiB for fp8-ada
instead of 553).

### Table 1 reproduction (`paper_table1()`; F_2^32 / F_2^128, |S| = 148, rate 1/4, SHA-256, no ZK)

| cells | paper | ours | dims k'_1..k'_L, final | L |
|---|---|---|---|---|
| 2^20 | 145 | 148 KiB (x1.02) | 6, 4; 2^10 | 2 |
| 2^24 | 255 | 243 KiB (x0.95) | 6, 4, 4; 2^10 | 3 |
| 2^28 | 360 | 356 KiB (x0.99) | 6, 4, 4, 4; 2^10 | 4 |
| 2^30 | 420 | 418 KiB (x1.00) | 6, 4, 4, 3, 3; 2^10 | 5 |

### Our five Table 2 cells (BabyBear / BabyBear^6, 2^-128 union bound, ZK salt + mask rows included)

Three points on the (level-1 rate, later rate) x L grid per cell (`params.recommend`): **S** = smallest proof (rates 1/4 then 1/16,
L = 4–5), **B** = *balanced* = smallest proof within 10 % of the fastest estimated prover (level-1 rate 1/2, later 1/4, L = 4–5) —
**the recommended set** — and **F** = fastest under 1 MiB (same rates, L = 3, large final vector).  Effective level-1 rates are 3/16
(S) and 3/8 (B, F) because the tall dimension is 3 x 2^k.  "today" = today's measured B-Ligero seconds/batch (0.781 / 0.665 / 0.356 /
0.252 / 0.0714 s); "est" = the op model at the throughput table (enc = butterflies at 0.5–0.7 T/s, mk = BLAKE3 at 300–500 GB/s, ar =
sumcheck + openings); x = ratio to today's op count in the same bucket.

| cell (device) | pt | proof/batch | bytes/s at today's t | est prover s (enc x, merkle x, arith) → bytes/s | coins | verifier 1-thread |
|---|---|---|---|---|---|---|
| bf16-ampere (A100) | S | 579 KiB | 0.76 MB/s | 0.685 (0.396 x2.9, 0.160 x2.17, 0.129) → 0.9 MB/s | 55 | 41 ms |
|  | **B** | **704 KiB** | 0.92 MB/s | 0.361 (0.146 x1.1, 0.063 x0.85, 0.152) → 2.0 MB/s | 51 | 102 ms |
|  | F | 888 KiB | 1.16 MB/s | 0.343 (0.134 x1.0, 0.060 x0.81, 0.149) → 2.7 MB/s | 48 | 140 ms |
| bf16-hopper (H100) | S | 579 KiB | 0.89 MB/s | 0.403 (0.244 x3.1, 0.096 x2.32, 0.063) → 1.5 MB/s | 55 | 40 ms |
|  | **B** | **704 KiB** | 1.08 MB/s | 0.202 (0.090 x1.2, 0.038 x0.91, 0.075) → 3.6 MB/s | 51 | 102 ms |
|  | F | 888 KiB | 1.37 MB/s | 0.192 (0.082 x1.1, 0.036 x0.87, 0.073) → 4.7 MB/s | 48 | 140 ms |
| fp8-hopper (H100) | S | 539 KiB | 1.55 MB/s | 0.197 (0.117 x2.9, 0.048 x2.25, 0.031) → 2.8 MB/s | 53 | 40 ms |
|  | **B** | **622 KiB** | 1.79 MB/s | 0.108 (0.048 x1.2, 0.021 x0.96, 0.039) → 5.9 MB/s | 53 | 47 ms |
|  | F | 769 KiB | 2.21 MB/s | 0.099 (0.043 x1.1, 0.019 x0.88, 0.038) → 7.9 MB/s | 46 | 137 ms |
| fp8-ada (RTX 4090) | S | 539 KiB | 2.19 MB/s | 0.285 (0.152 x2.6, 0.080 x2.03, 0.052) → 1.9 MB/s | 53 | 40 ms |
|  | **B** | **622 KiB** | 2.53 MB/s | 0.161 (0.063 x1.1, 0.034 x0.87, 0.064) → 4.0 MB/s | 53 | 47 ms |
|  | F | 769 KiB | 3.12 MB/s | 0.149 (0.056 x1.0, 0.031 x0.79, 0.062) → 5.3 MB/s | 46 | 138 ms |
| fp4-nvf4 (RTX 5090) | S | 461 KiB | 6.61 MB/s | 0.049 (0.025 x2.9, 0.015 x2.41, 0.009) → 9.7 MB/s | 47 | 47 ms |
|  | **B** | **532 KiB** | 7.63 MB/s | 0.027 (0.010 x1.2, 0.006 x1.03, 0.011) → 19.8 MB/s | 47 | 57 ms |
|  | F | 599 KiB | 8.59 MB/s | 0.025 (0.009 x1.0, 0.006 x0.95, 0.010) → 24.3 MB/s | 44 | 76 ms |

Today: 66 MB / 262 MB/s (fp8-ada), 126 MB / 161–177 MB/s (bf16), 60 MB / 169 MB/s (fp8-hopper), 15 MB / 210 MB/s (fp4).  So **~100x
fewer bytes per batch and 40–100x less egress at the same prover speed**; the ≤ 1 MB target holds for every cell at every point, the
≤ 10 MB/s target holds at today's prover times everywhere and at the *estimated* Ligerito prover times everywhere except fp4-nvf4
(0.027 s/batch x 532 KiB = 20 MB/s — fp4 is bandwidth-limited by how fast the 5090 proves, not by the proof; if 10 MB/s is a hard cap
there, use S = 461 KiB or accept a 20 ms/batch idle).

Proof byte breakdown, fp8-ada B (622 KiB): opened rows 256 (L1: 239 x 64 x 4 B = 60 KiB; L2–L5: 173–176 x 16 (8) x 24 B) + Merkle
paths 334 (E[siblings] at n = 2^25 .. 2^12, 32 B, + one 32 B salt per opened leaf under ZK) + PCS sumcheck 1.4 + final vector 768 x 24 B
= 18 + relation messages 13.4 KiB.  Merkle paths are 54 %; the only big lever left is the query count (list decoding: ~90 instead of
172–239 queries at 2^-128, about -200 KiB, needs the list-decoding proximity-gap argument for the DP24 term — flagged, not designed
today).  **The byte model is validated against the prototype's measured proofs**: ligerito-proto's eight 4090 runs (Table A 2^26/28/29
at |S| = 192; Table B: my pow2 F point at 2^29 and 2^30, my S point at 2^29, paper-style ℓ = 3/4) measure 454/532/581/790/911/508/
1030/558 KB and `params.py` predicts 454/531/581/790/911/507/1028/558 KB (`test_byte_model_matches_measured_prototype`, ≤ 1 %).  §9's
"design's byte model over-predicts 20–30 %" refers to proto's own no-dedup predictor, not to `params.py`.

## For ligerito-proto

Parameter sets (paper notation `(ℓ = L + 1, k_i, k'_i, |S_i|)`; `tall_i = 3 x 2^{k_i - k'_i}` with the ternary variable; the `pow2` line is what
to run on the prototype's power-of-two harness):

~~~
fp8-ada / fp8-hopper  (cells = 4096 x 3 x 2^16 = 3 x 2^28)
  S: L = 5   L1 tall 3x2^22 x 64  (k'=6, n=2^26, eff. rate 3/16, |S|=172)   L2 3x2^18 x 16 (k'=4, n=2^24, rate 3/64, |S|=140)
             L3 3x2^14 x 16 (k'=4, n=2^20, |S|=140)   L4 3x2^11 x 8 (k'=3, n=2^17, |S|=140)   L5 3x2^8 x 8 (k'=3, n=2^14, |S|=140)
             final 768 ext.                                                          539 KiB, 53 coins, 2^-128.02
  F: L = 3   L1 3x2^21 x 128 (k'=7, n=2^24, eff. rate 3/8, |S|=239)   L2 3x2^16 x 32 (k'=5, n=2^20, rate 3/16, |S|=172)
             L3 3x2^11 x 32 (k'=5, n=2^15, |S|=174)   final 6144 ext.                769 KiB, 46 coins
  pow2 (N = 2^30, cols padded to 2^18): S: L1 2^24 x 2^6 (n=2^26, 1/4, |S|=191), L2 2^20 x 2^4 (n=2^24, 1/16, 143), L3 2^16 x 2^4 (143),
             L4 2^13 x 2^3 (143), L5 2^10 x 2^3 (144), final 2^10 — 569 KiB (proto measured 508 KB at 2^29 for the same rates).   F: L1 2^23 x 2^7 (n=2^24, 1/2, |S|=311), L2 2^18 x 2^5 (1/4, 191),
             L3 2^13 x 2^5 (193), final 2^13 — 924 KiB (proto measured 911 KB).
bf16-hopper / bf16-ampere  (cells = 3 x 2^29):  S: L1 3x2^23 x 64 (n=2^27, |S|=174), L2 3x2^19 x 16 (n=2^25, 139), L3 3x2^15 x 16 (139),
             L4 3x2^11 x 16 (140), L5 3x2^8 x 8 (141), final 768 — 579 KiB.  F: L1 3x2^21 x 256 (n=2^24, 3/8, 239), L2 3x2^16 x 32 (172),
             L3 3x2^11 x 32 (174), final 6144 — 888 KiB.
fp4-nvf4  (cells = 3 x 2^26):  S: L1 3x2^20 x 64 (n=2^24, 172), L2 3x2^16 x 16 (n=2^22, 139), L3 3x2^12 x 16 (140), L4 3x2^9 x 8 (140),
             final 1536 — 461 KiB.  F: L1 3x2^19 x 128 (n=2^22, 239), L2 3x2^14 x 32 (172), L3 3x2^10 x 16 (174), final 3072 — 599 KiB.
~~~

* **Recommended (B)**: fp8 (both): L = 5, L1 3x2^22 x 64 (n = 2^25, eff. rate 3/8, |S| = 239), L2 3x2^18 x 16 (n = 2^22, rate 3/16,
  173), L3 3x2^14 x 16 (n = 2^18, 174), L4 3x2^11 x 8 (n = 2^15, 174), L5 3x2^8 x 8 (n = 2^12, 176), final 768 — 622 KiB, 53 coins.
  bf16: L = 4, L1 3x2^22 x 128 (n = 2^25, 3/8, 239), L2 3x2^18 x 16 (n = 2^22, 173), L3 3x2^14 x 16 (173), L4 3x2^10 x 16 (n = 2^14, 175),
  final 3072 — 704 KiB, 51 coins.  fp4: L = 4, L1 3x2^20 x 64 (n = 2^23, 239), L2 3x2^16 x 16 (173), L3 3x2^12 x 16 (173), L4 3x2^9 x 8
  (175), final 1536 — 532 KiB.  pow2 harness equivalents: `our_params(rel, L, rate_log2=(1,2,2,2,2), radix3=False)`.
* Your |S| = 192 at rate 1/4 gives 2^-130.2/level, fine; the calculator's allocation is 172 (level 1, eff. rate 3/16) / 140 (rate 1/16 levels)
  for the same union. Get exact numbers with `python -m backends.direct.ligerito.params` or
  `params.our_params(params.RELATIONS["fp8-ada"], L=5, rate_log2=(2,4,4,4,4))` (`.proof_bytes()`, `.soundness()`, `.coins()`,
  `.prover_ops()`, `.latency(rtt, prover_s, inflight_bytes, mem)`); `radix3=False` for the pow2 shapes.
* Confirmed from my side: `F_p[x]/(x^6 - 31)`, coefficient-basis RS on `<w_n>`, encode along the tall axis, column-major `x = row + R·col`,
  tensor-claim representation of opened rows, and your Coins call order. ref.py follows exactly this (any deviation will be listed here).
* Level-1 NTT length is 2^26 (S) or 2^24 (F) for fp8; 2^27 / 2^24 for bf16 — the S point needs your 4-step NTT at 2^26–2^27; if 2^27 does
  not fit the 4090 (message 6.4 GB + codeword 34 GB if materialised), do NOT materialise the level-1 codeword: hash the Merkle leaves
  streaming out of the NTT and recompute the |S_1| opened rows afterwards as a (wide x tall) x (tall x |S_1|) base-field GEMM
  (`openings_recompute_base_ops` = |S_1|·N = 1.4e11 MACs, ~30 ms on the 4090) — that is what the F/S time estimates assume.
* Prover budget the estimates imply (fp8-ada, 4090, S point): encode 0.152 s (7.6e10 butterflies), Merkle 0.080 s (24 GB hashed), sumcheck +
  openings 0.049 s → 0.28 s vs today's 0.252 s; F point: 0.056 + 0.031 + 0.060 = 0.147 s. Level 2 at rate 1/16 is 25 % of the encode
  (n_2 = 2^24 x 16 ext columns) — if encode is the bottleneck, use rate 1/4 there (rates (2,2,2,2): 597 KiB, encode x1.93 instead of x2.64).

## Interface

* `params.LigeritoParams(tall1, wide_log2, rate_log2, queries, fields, target_log2, zk, relation, pcs_radix_log2)`; `RelationShape` for each
  Table 2 relation in `params.RELATIONS` (rows/rows_pad/cols/lin/quad/nnz/lookups from `compile` of the real systems, counted 17:20Z).
* `ref.py` (landed 18:20Z): `Dims(tall, wide_log2, n_log2, queries)` (`Dims.from_params(p)`, `Dims.toy(log_n, L)`), `commit(f, dims) ->
  ProverState` (`.root` = the commitment), `prove_eval(state, w, coins) -> Proof`, `verify(root, w, value, proof, coins) -> (bool,
  reason)`, `point_tensor(z, dims.radices)` (eq on binary digits, Lagrange-3 on the ternary digit 0), `mle_eval`, `FSCoins(seed)`,
  `proof_to_dict / proof_from_dict / fixture` (JSON).  The module docstring is the spec (layout, RS, Merkle, claim batching, coin order,
  transcript hashing).  Statement = a *tensor claim* `<f, (x) w_j> = v` — the sumcheck lane's `1 + n_links` evaluation claims are exactly
  such tensors (`eq(z, .)` split into row / column digits), batched by the PCS with the opened-row claims at level 2 for free.
* Deviations from the proto's 17:45Z note, for the Rust verifier to follow ref.py: (1) ref.py's verifier computes the "expected symbols"
  `y_s = <row_s, rbar>` itself (nothing sent) — 14 KiB less; (2) codeword positions are in NATURAL order (`row s` holds `P(w_n^s)`);
  the proto's 4-step NTT stores `P(w^{k' + n2 k1})` at `s = k' n1 + k1` — permute at leaf-hashing time or tell the verifier the map;
  (3) the query coin for level `i-1` is drawn right after `root_i` (before that level's batching / sumcheck), which is the sound order;
  (4) the transcript is BLAKE3-only (chain + XOF, u64 mod p) so the Rust side needs one hash; if proto keeps BLAKE2b + SHAKE, the
  fixtures differ ONLY in the coins — either is fine, but pick one before 21:00Z; (5) a ternary digit 0 (`tall = 3 x 2^k`) is supported
  end to end (tests), so the radix-3 shapes above need no column padding.

## IR requests

(none yet)

## 2. D2 — the reference PCS (`ref.py`)

What it fixes (the module docstring is normative): mixed-radix index with digit 0 least significant (binary digits, optional ternary
digit 0); column-major level matrices (rows = low digits) so tensors split for free; coefficient-basis RS along the tall axis on `<w_n>`
in natural order; BLAKE3 leaves = the codeword row as LE u32 (base: `wide` words; ext: `6 wide` words), nodes = BLAKE3(l || r), batched
multi-opening in the canonical order (`merkle_multi_open`); the claim list `(gamma_t, a_t, b_t)`, the degree-2 partial sumcheck with
3-coefficient messages (low digit first), carried terms `(gamma_t b_t~(r), a_t)`, alpha-batching with the opened-row tensor claims;
the final vector checked directly.  Verifier work per level: `k'` sumcheck rounds, `T x k'` ext mults for the `b~(r)`, `|S| x wide` for the
`y_s`, `|S| log n` hashes; at the end `T x tall_L + |S_L| x tall_L` ext mults.  Everything the Rust verifier needs is in
`proof_to_dict` + the statement (`z`, `value`, `commitment`) + `FSCoins`.

Toy timings (laptop, numpy): N = 2^12, L = 3, 8 queries: 0.4 s prove+verify; the tests are 3 s total.

## 3. D3 — design: §2 items 1–6, with mechanisms and costs

Numbers below are fp8-ada at point **B** on the RTX 4090 (bf16-hopper B on the H100 in brackets) unless said otherwise; formulas and
inputs are in `params.py` (`prover_ops`, `verifier_ops`, `coins`, `latency`, `soundness`, `ligero_today_ops`).

### 3.1 Item 1 — chain / wide constraints: a shift, done as one small extra sumcheck (no permutation argument)

Facts from `compile.py` / `chain.py`: fp8-ada has 3 linked rows (`c.s, c.t, c.f`: the running exponent-sum / tally / flag carried from
unit `j` to unit `j+1` inside a VU of 48 units; the link is broken at VU boundaries by the `link/start/end` 0/1 masks); `wide` groups are
only a hint partition — `wide.py` already splits the wide adders into limb identities that are ordinary `Linear` rows.  So "wide" costs
nothing new; "chain" is: `link(c) . (W(c_x, next(c)) - Y_x(W(:, c))) = 0` for `n_links = 3` rows.

Mechanism (agreed with ligerito-sumcheck's 17:20Z design; theirs is the measured one): treat `Wnext_x(c) = W(c_x, succ(c))` as a
*virtual row* of the column vector `z_j` inside the zero-check (so every constraint stays `A(z) B(z) = C(z)` with scalar coefficients),
and prove the `n_links` values `Wnext_x~(r_c)` the prover claims at the end of the rows-sumcheck with one more degree-2 sumcheck over
the `n_c = 18` column variables:

~~~
sum_x gamma^x Wnext_x~(r_c)  =  sum_c succ~(r_c, c) . V(c),     V(c) = sum_x gamma^x W(c_x, c),
succ~(r, c) = eq(r, pred(c))   (the eq table rolled by one along j; cyclic inside a sub-batch -- the wrap is never a link)
~~~

ending in `n_links` point claims `w~(bits(c_x), rho)` on the committed polynomial (tensor claims: batched into the PCS with the others
for free) and the verifier's closed-form evaluation of the cyclic-successor MLE `succ~(r_c, rho)` in `O(n_j^2)` ext mults (the
"shifted-polynomial identity").  The "sparse-matrix" alternative (Ligero's general linear test with the shift matrix, as a sumcheck) has
the same prover work — the rolled eq table IS `A~(r, .)` — and an `O(l)` verifier; both are cheap to keep.

Cost: prover = one table `V` of `C = 2^18` ext entries (`n_links x C` ext-by-base MACs = 5e6 base-mult-eq) + 18 degree-2 rounds over it
(`~3 x 2 x C` ext ops ≈ 5.7e7 base-eq): **< 0.1 % of the zero-check**; proof: `18 x 3 x 24 B = 1.3 KB` + 3 claims; coins: 18 (9 at c = 2,
6 at c = 3); verifier: `O(n_j^2) = 200` ext mults.  Why not a permutation/equality argument: it would add a grand-product (degree +1,
inverses or a running product over `N` cells) for a coupling that is a fixed linear map; the STARK "next row" trick IS this sumcheck
when the coupled axis is the low variables (the sumcheck lane lays `j` in the low 14 bits for exactly this reason).

### 3.2 Item 2 — lookups: carry over as degree-2 rows; LogUp is a Phase-C option

`compile.lookup` = one-hot `sel` rows over the table's distinct rows (26–31 per `POW/ALIGN/LEAD/NORM` table), `sum sel = 1` (Linear),
`sel_i (sel_i - 1) = 0` and key selection (Quadratic), plus the key's range bits (`bit` rows).  Every one of these is already a
`Quadratic`/`Linear` row, i.e. a degree ≤ 2 term of the batched zero-check (degree 3 after `eq`), so **nothing changes** in the
sumcheck; the cost is the rows themselves (they are in the 3532 Q + 589 L count).  LogUp (`sum_i 1/(alpha - key_i) = sum_t m_t / (alpha - t)`)
would replace the ~30 selector rows per lookup by 1–2 rows (inverse + multiplicity) but adds a fractional-sum sumcheck (degree 3–4 with
a running-sum layer over `N` cells, ~2x the zero-check's later-round work) and a second challenge round; not worth it today — the
proof is not row-bound (rows enter only through `wide_1 = 64` PCS columns and the final vector), and the prover's encode does not
care what the rows mean.  Keep one-hot; revisit if the zero-check's table (`K x C`, §3.5) is the memory bottleneck.

### 3.3 Item 3 — ZK for the sumcheck + the openings (malicious verifier, live coins) — three sentences, then the cost

(1) A uniformly random **mask column** (the top level-1 PCS column, = relation rows 4032–4095, all padding in fp8-ada and bf16) makes the
folded vector `v_1 = M_1 rbar` uniform and independent of the witness (`rbar[63] = prod r_j != 0`), so every later message — levels ≥ 2
sumchecks, opened rows, the final vector, and the evaluation claims themselves — is a function of a uniform vector and public coins and
is simulated by sampling it.  (2) Per level-1 column, `|S_1| = 239` **consecutive** random coefficients (placed in the cells of pad
sub-batch 15, `j < 239`, which the zero-check excludes through the public activity indicator `act(c)` folded into its eq weight) make
the 239 opened symbols of that column uniform (the opened-position x coefficient-position submatrix of the RS generator is a scaled
Vandermonde in 239 distinct points, hence invertible), and one more random cell per column at a row where the eq row-part is non-zero
(**A-cell**) makes the level-1 partial-sumcheck's per-column values `u[c]` uniform — together 64 x 240 = 15 k mask cells, all inside
padding.  (3) The zero-check's `3 n_vars + 1` partial sums are hidden **Libra-style**: the prover commits (Merkle, 91 ext coefficients)
a random `g` with `sum_cube g = 0`, the verifier adds `rho . g` to the sumcheck, `g(r)` is opened at the end; all coins are the
verifier's (8c), so the simulator samples masks + coins and replays.  ligerito-zk's 17:55Z note reaches the same design (mask column,
A-cells) from the leak table; their `zk.py` owns it.  Cost: 0 extra cells (padding rows hold everything: 319 x 2^18 = 84 M cells free vs
12.6 M + 15 k needed), +91 x 24 B + 32 B root + 1 coin for `rho`, prover +`N` ext-by-base MACs for `g` (0.2 % of the zero-check), verifier
+91 ext mults; the `act(c)` indicator costs the verifier one 16-entry MLE.  What plain Ligerito leaks without it: `2^11` independent
linear functionals of `f` per proof (35 % of our witness cells are structured zeros — distinguishable from the trivial witness).

### 3.4 Item 4 — interactive rounds vs a live verifier at 30 ms RTT

Coins per batch (sequential verifier messages on the prover's critical path; `params.coins()`), fp8-ada B:

| packing (variables per coin) | zero-check (30 vars, deg 3) | rows (12) + shift (18) | PCS sumchecks (k' = 6,4,4,3,3) | PCS query/batch coins (2L−1) | τ/ρ | **total** | extra bytes |
|---|---|---|---|---|---|---|---|
| c = 1 | 30 | 30 | 20 | 9 | 1 | **90** | 0 |
| c = 2 | 15 | 15 | 11 | 9 | 1 | **51** | +6 KB |
| c = 3 | 10 | 10 | 7 | 9 | 1 | **37** | +25 KB |

(`params.py`'s 53 is the c = 2 row with my own folding of the constraint index; the sumcheck lane's `k`-then-`c` binding order is the
first row's 30 + 30.)  A `c`-variable round sends the round polynomial on the grid `{0..d}^c` (`4^c` ext for degree 3, `3^c` for degree
2) and costs the prover `~(d+1)^c / (c (d+1))` more evaluations per streamed table element — fine for c = 2 everywhere and c = 3 after
the first zero-check round (tables 4x smaller).

Latency: `wait = coins x RTT = 1.1–1.6 s` per batch against `T_p ≈ 0.16 s` (B, 4090) [0.20 s bf16 H100].  Hiding it needs
`depth = ceil((wait + T_p)/T_p) = 8–11` batches in flight; each holds the level-1 message (3.2 GB base) + Merkle leaves (1.1 GB) = 4.3 GB
[6.4 + 2.1 GB], so the 4090 fits 5 (with the codeword dropped after hashing and re-derived for the openings, §3.5), the H100 80 GB fits
9 [7].  Consequence (`params.latency`): 4090 at 30 ms → 0.35 s/batch = **1.7–2.2x slower than compute-bound**; H100 → compute-bound
[bf16: 0.23 s vs 0.20].  Ways out, in order of preference: (a) **same-DC verifier** (1 ms RTT): wait 0.05 s, depth 2, no loss — the
verifier's coin box is a CPU pod next to the prover (live-2's CCOM/coin-stream design applies unchanged; the trust model is the box's
owner, not its location); (b) c = 3 packing: 37 coins, 1.1 s, depth 8 — fits the H100, not the 4090; (c) FS for the *sumcheck rounds
only*, live coins for the 10 query/batching/τ coins: 0.3 s wait, depth 3 — but see §3.5's FS caveat: with `|F| = 2^185` the FS'd rounds
cost up to `Q . rounds . 3/|F| ≈ 2^64 . 2^6 . 2^-183.8 = 2^-114` under the 2^64-query random-oracle model, which breaks the 2^-128 budget
on paper (a degree-8 extension, 2^247, would fix it at 1.33x the ext cost); (d) batching several batches into one sumcheck (coins per
batch / B) trades memory for latency — same constraint as depth.  Recommendation: (a) for the device runs, (b) as the default packing,
(c) only if the user accepts the RO bound.

### 3.5 Item 5 — soundness (PROTOCOL.md §6 style), fp8-ada B and bf16-hopper B

Statement: the prover convinces the verifier that a committed `f` (one BabyBear vector of `N = 3 x 2^28` [3 x 2^29] cells) satisfies the
`4121` [3503] batched constraints on every active column and that the claimed public outputs are its `y16` / digests.  Errors, each a
probability over the verifier's coins in `F = F_{p^6}`, `log2 |F| = 185.44`; a cheating prover wins if ANY event happens, so the union:

~~~
Zero-check (Spartan-style):
  ZC.1  constraint batching  (Q + Lin)/|F|            = 4121 / 2^185.4          = 2^-173.4     [3503: 2^-173.7]
  ZC.2  eq(tau) Schwartz-Zippel  n_vars/|F|           = 30 / 2^185.4            = 2^-180.5
  ZC.3  sumcheck  3 . 30 / |F|  (+7 ternary, +4 mask) = 2^-178.8
  ZC.4  rows sumcheck 2 . 12/|F|, shift 2 . 18/|F|    = 2^-180.5, 2^-180.3
  ZC.5  claim batching (1 + n_links + masks) / |F|    = 2^-182
PCS, level i (paper (17), unique decoding, e_i = (n_i - tall_i)/2, per-query pass prob (1 + rate_i)/2):
  L1  (11/16)^239 = 2^-129.2   + k'_1 n_1/|F| = 6 . 2^25 / 2^185.4 = 2^-157.9   + 2 k'_1/|F| = 2^-181.9
  L2  (19/32)^173 = 2^-130.1   + 4 . 2^22/|F| = 2^-161.4                          + 2^-182.4   + (|S_1|+1)/|F| = 2^-177.5
  L3  (19/32)^174 = 2^-130.9   + 2^-165.4 + 2^-182.4 + 2^-178.0
  L4  (19/32)^174 = 2^-130.9   + 2^-168.9 + 2^-182.9 + 2^-178.0
  L5  (19/32)^176 = 2^-132.4   + 2^-171.9 + 2^-182.9 + 2^-178.0
  [bf16 B: L1 (11/16)^239 = 2^-129.2, L2 (19/32)^173, L3 173, L4 175; field terms <= 2^-157]
Union:  2^-128.01  [2^-128.05]   -- the five (four) proximity terms are the whole budget; every field term is below 2^-157.
~~~

Reading: `k'_i n_i / |F|` is the paper's log-randomness (DP24/DG24) term for folding the `2^{k'_i}` columns with the tensor
`rbar` instead of a uniform vector — with 25+ bits of slack its exact constant is irrelevant (my PDF copy was garbled; the term is
transcribed from the formula's structure and docs.rs; **someone with a clean copy should confirm (17)**, it cannot change the parameter
choice unless it is `> 2^-150`).  Unique decoding is what makes the per-query term `(1 + rate)/2`; list decoding (Johnson) would give
`~ sqrt(rate)`-type terms and ~half the queries, at the price of the list-size factor in the batching — not used.  Interactive coins:
no Fiat-Shamir loss; if the sumcheck rounds go FS (§3.4 c), add `Q . 66 . 3/|F| = 2^-114` at `Q = 2^64` — that term, not the PCS, would
then set the security level.  ZK adds no soundness term (masks are committed cells; `act(c)` is public).

### 3.6 Item 5' — prover op count vs today's B-Ligero (three buckets), same units

Units: NTT butterflies; BLAKE3 bytes; base-multiply equivalents (ext x base = 6, ext x ext = 36).  Today's formulas from PROTOCOL.md
§4/§8 per sub-batch (`m = 3769, l = 16384, n = 4l, D = 6`, 12 sub-batches); Ligerito's from `prover_ops` (B: L1 `3x2^22 x 64`, n = 2^25).

| bucket | today (fp8-ada, 4090) | Ligerito B | ratio | Ligerito B est. time |
|---|---|---|---|---|
| **encode** | `m (l/2 log l + n/2 log n) x 12` = 2.9e10 butterflies | `64 . 2^24 . 25` (L1) + `16 . 2^21 . 22 . 6` (L2, ext) + … = 3.15e10 | **x1.09** | 0.063 s at 0.5 T/s |
| **Merkle** | `4 m n x 12` = 11.9 GB hashed | `2^25 . 64 . 4` + `2^22 . 16 . 24` + … = 10.3 GB | **x0.87** | 0.034 s at 300 GB/s |
| **tests → sumcheck** | `2 D m n + (Q + nnz) n + 20 D n` x 12 = 5.3e10 base-eq (measured `t.arithmetic` 0.129 s) | zero-check 9.1e10 (round 1: `C/2 x 2 F-evals x (Q + nnz)` = 4.4e9 base; fold 2.2e9; rounds ≥ 2 in ext 8.4e10) + rows/shift 1.3e8 + PCS partial sumchecks `3N + 3 sum tall` = 1.6e10 + carried-claim contractions `sum_i (sum_{j<i}|S_j|) tall_i wide_i` (ext x base) = 2.0e10 + **openings 1.9e11** (`|S_1| . N` base MACs, Horner/GEMM at 239 points — only if the level-1 codeword is not kept) = 1.3e11 (codeword kept) / 3.2e11 (recomputed) | x2.4 / x6.0 in op count | 0.02–0.06 s at 5 T base-eq/s; **0.1–0.3 s if it runs at today's measured effective rate (4e11/s, memory-bound)** |
| serialization | 66 MB (`t.serialization`) | 0.62 MB | x0.01 | ~0 |
| **total** | 0.252 s measured | | | **0.16 s (model) – 0.35 s (memory-bound arithmetic)** |

Memory (why the openings are recomputed on the 4090): level-1 codeword 8.6 GB + level-1 message 3.2 GB + zero-check tables after
round 1 (`3 x K/2 x C x 24 B` = 8.9 GB in the K x C formulation; the codeword must live until the level-1 queries, i.e. after the
zero-check) = 20.7 GB > what a 24 GB card can pipeline; dropping the codeword after hashing and re-deriving the 239 opened rows costs
1.9e11 base MACs — a `(239 x 12.6M) . (12.6M x 64)` int32 Montgomery GEMM, ~30 ms on the 4090 (fp64-limb GEMMs are NOT an option there:
1.3 TFLOPS).  The H100 (80 GB) keeps the codeword.  Point S (rate 1/4, 539 KiB) costs encode x2.6 / Merkle x2.0 — the tall-axis NTT
is 2^26 long at effective rate 3/16 — which is why B is the recommendation: **parity with today's encode + Merkle, 100x smaller proofs**;
the arithmetic bucket is the one to measure (ligerito-sumcheck), not the encode.

### 3.7 Item 6 — verifier cost, and what the Rust verifier does per batch (B, fp8-ada)

`verifier_ops`: `sum_i |S_i| (wide_i + log2 n_i hashes + 3)` = 239 x 64 + 173 x 16 x 3 + 174 x 8 x 2 ≈ 27 k ext-by-base / ext mults for the
`y_s` + 13.8 k BLAKE3 for the multi-paths; sumcheck rounds `sum k' x 3` = 60 ext mults; `b~(r)` for the carried terms `T x k'` with `T`
growing to `1 + 4 + sum_{i<5} |S_i| = 937`: 20 k; the final vector: `(T + |S_5|) x tall_L` = `(937 + 176) x 768` = **0.85 M ext mults**
(dominant; halve it by pre-summing the carried tensors' digit-0 factors); relation side: `alpha = eq(r_k)^T A` = nnz = 19 k, the public
MLEs at `r_c` (y16 + 16 digest words per VU) = 70 k, `succ~` 200.  Total ≈ 0.96 M ext mults + 14 k hashes ≈ **47 ms single-thread Rust**
(40 ns per BabyBear^6 mult; ~6 ms on 8 threads) [bf16 B: 102 ms, final vector 3072].  Bytes read: 622 KiB.  Today's `ligero-verify`
re-encodes 197 columns of 3769 rows per sub-batch from a 66 MB proof — Ligerito's verifier is I/O-trivial and ~10x less arithmetic.

### 3.8 Phase B work breakdown (hours; lanes as in the wave-B brief §1)

| # | item | lane | h |
|---|---|---|---|
| 1 | `pcs.py` at real shapes: B parameters from `params.py`, radix-3 tall (or pow2 padding), 4-step NTT to 2^25 (2^26 for S), Merkle leaves streamed out of the NTT, openings by recompute (GEMM) on 24 GB cards, ref.py bit-parity at toy dims | ligerito-proto | 10 |
| 2 | layout + zero-check (K x C tables, Gruen, c = 2 packing, `act(c)`) + rows + shift sumchecks, negatives, measured at fp8-ada 4096 VUs and bf16 | ligerito-sumcheck | 14 |
| 3 | `zk.py`: mask column + consecutive mask cells + A-cells inside padding, Libra `g`, simulator test, `omitted`/`zk_statement` | ligerito-zk | 10 |
| 4 | `transcript.py` c-variable packing + `LiveCoins` per-batch coin stream + pipeline depth N + same-DC verifier option, latency table | ligerito-proto / live-2 | 8 |
| 5 | `proof.py` (LGTO0001: header, roots, per-level rows/siblings/coeffs, final, relation messages ≈ 622 KiB), `prove.py`, `run.py`, bench-result/v1, gates, relchain parity | ligerito-relation | 10 |
| 6 | Rust: ext field + PCS verifier from ref.py fixtures (8) + sumcheck/shift verifier (6) + proof reader + `batch` CLI (4) + perf pass (2) | ligerito-verify-rs | 20 |
| 7 | red-team negatives across modules (fold inconsistency, wrong query set, mask removal, act(c) abuse), DISCREPANCIES | red-team-leaf | 6 |
| 8 | integration + Table 2 on the five devices (bytes, bytes/s, three prover buckets, verify ms) | ligerito-relation + device wave | 8 |
|  | **total** | | **86** |

Critical path (2 → 5 → 6-sumcheck → 8) ≈ 38 h of work; with six lanes in parallel the realistic 04:00Z state is: PCS at real N, zero-check
measured, Rust PCS verifier green on fixtures, one non-ZK end-to-end fp8-ada batch; ZK integration and the five-device table are the
parts most likely to slip past 04:00Z.

## 4. Top risks (with what would change)

1. **Zero-check memory/time at real N.**  `K x C` tables = 3 x 4096 x 2^18 x 4 B = 12.9 GB base, 38 GB in the extension after round 1 (the
   sumcheck lane's formulation) — must be chunked along `c` on the 4090 (fine: the round-1 sum is separable over `c`), but if it runs at
   today's memory-bound rate the arithmetic bucket is 0.1–0.3 s, not 0.06 s, and the 4090 total becomes 0.25–0.4 s (parity to 1.6x
   today).  Mitigation: keep the `k`-first binding order (tables shrink fastest) but evaluate round 1 straight from the sparse
   `A, B, C` without materialising the base tables (`4.4e9` base ops instead of a 12.9 GB write), and chunk the ext tables along `c`.
2. **Coin latency on 24 GB cards.**  51–53 coins x 30 ms needs depth 9; the 4090 fits 5 → 1.7–2.2x throughput loss unless the verifier's
   coin box is in the same DC (§3.4 a) or the H100 is used.  This is a deployment decision, not a protocol one.
3. **Soundness constants transcribed, not read.**  The per-level field term and the unique-decoding per-query term were reconstructed
   from a garbled PDF, docs.rs and the Table 1 fit (which matches to 5 %, so the *query* term is right); if the batched tensor claims
   need a list-decoding-style factor at level 1, `|S_1|` grows ≤ 1.5x (+60 KiB rows, +80 KiB paths).  Ask anyone with a clean PDF to
   check (17) against `soundness()`'s `formula` strings.
4. (proof floor) Merkle paths are 54 % of the proof at 32 B digests; 16 B digests are not acceptable at 128 bits; the next lever is
   fewer queries (list decoding) — a paper-reading task, not an engineering one.

## 5. Is §2's hypothesis right?

In structure, yes.  Corrections with numbers: (a) "prover ≈ our RS encode" holds only at level-1 rate **1/2** (B: encode x1.09, Merkle
x0.87); at the paper's 1/4 the tall-axis NTT is 2^26–2^27 long at effective rate 3/16 and encode is x2.6–3.1 — the proof gain from 1/4 is
83 KiB (622 → 539), not worth 2.4x the encode.  (b) Proof 0.3–1 MB ✓ (539–704 KiB predicted, 508–911 KB measured by proto), but its composition is 54 % Merkle paths, 41 %
opened rows, 3 % final vector, 2 % relation messages — `sum |S_i| 2^{k'_i} 4 B` alone is 1/3 of it.  (c) "One degree-3 sumcheck pass
over N cells in the extension" is right in FLOPs (1e11 base-eq) but wrong in bytes: after round 1 the tables are 6x wider — the
zero-check is a memory-bandwidth problem (§4.1), and the level-1 codeword vs zero-check tables vs pipelining depth is the memory
budget that decides 4090 throughput.  (d) 40–60 coins ✓ (51 at c = 2; 37 at c = 3; 90 unpacked).  (e) Chain/wide need no permutation
argument: one degree-2 sumcheck with the cyclic-successor MLE, < 0.1 % of the prover; lookups carry over unchanged.  (f) The
verifier is 47 ms single-thread, dominated by the final-vector checks, not by hashing.

## For ligerito-sumcheck
* Your layout (`x = i (S l) + s l + j`, rows high) is compatible with the PCS as long as the PCS's level-1 "rows" are the LOW 24 bits
  (`j, s, i mod 64`) — the PCS does not care what the bits mean; your `1 + n_links` claims are tensors `eq(z, .)` split at bit 24.
  If you keep `S = 16` (pow2 padding) the PCS shapes are the `pow2` lines in `## For ligerito-proto` (569–924 KiB; measured 508–911 KB); the radix-3 shapes
  need `S = 12` with the ternary digit LOW (`x = d + 3 x'`), which your `s` axis is not — so pow2 it is unless you move `s`.
* Please fold a public activity indicator `act(s)` (1 for real sub-batches) into the zero-check's eq weight so the ZK mask cells can
  live in pad sub-batch 15 (§3.3); it is one 16-entry MLE for the verifier.
* Round-1 of the zero-check straight from the sparse `A, B, C` (no `K x C` materialisation) is the difference between 4.4e9 ops and
  a 12.9 GB write on the 4090.

## For ligerito-zk
* §3.3 above is my version of your design; the consecutive-coefficient argument (scaled Vandermonde) is what makes 239 mask cells per
  column sufficient for the opened rows; the A-cell needs `eq_low(z)[q] != 0` at its row `q` — pick `q` in the pad sub-batch too.

## For ligerito-verify-rs
* Fixtures: `python -m backends.direct.ligerito.ref > /tmp/ligerito_fixtures.json` (4 cases: 1/2/3 levels binary, 2 levels radix-3;
  155 KB).  Everything is in `ref.py`'s docstring + `FSCoins`; the negatives in `test_ref.py` are the ones to port.

## IR requests
* none required.  Nice-to-have for Phase C: a `System` flag marking rows that are pure padding / never referenced (so `zk.py` can pick
  mask cells without re-deriving it from the layout), and per-lookup `sel` row groups exposed as a list (for a future LogUp).

## FINAL (18:25Z) — for the coordinator

**Parameter sets (recommended = B; `params.recommend(rel, gpu)["balanced"]`)** — level-1 nominal rate 1/2 (effective 3/8 with the
ternary tall digit), later levels 1/4, 2^-128 union bound, ZK salts + masks counted:

~~~
fp8-ada / fp8-hopper (3 x 2^28 cells): L = 5; L1 3x2^22 x 64 (n=2^25, |S|=239), L2 3x2^18 x 16 (n=2^22, 173), L3 3x2^14 x 16 (n=2^18, 174),
    L4 3x2^11 x 8 (n=2^15, 174), L5 3x2^8 x 8 (n=2^12, 176); final 768 ext            -> 622 KiB, 53 coins, verifier 47 ms (1 thread)
bf16-hopper / bf16-ampere (3 x 2^29): L = 4; L1 3x2^22 x 128 (n=2^25, 239), L2 3x2^18 x 16 (173), L3 3x2^14 x 16 (173), L4 3x2^10 x 16 (175);
    final 3072                                                                          -> 704 KiB, 51 coins, verifier 102 ms
fp4-nvf4 (3 x 2^26): L = 4; L1 3x2^20 x 64 (n=2^23, 239), L2 3x2^16 x 16 (173), L3 3x2^12 x 16 (173), L4 3x2^9 x 8 (175); final 1536
                                                                                        -> 532 KiB, 47 coins, verifier 57 ms
smallest (S: rates 1/4 then 1/16): 539 / 579 / 461 KiB at encode x2.6-3.1;  fastest under 1 MiB (F: L = 3): 769 / 888 / 599 KiB.
~~~

**Predicted proof bytes/batch and bytes/s per Table 2 cell (B; S and F in §1's table)**: bf16-ampere 704 KiB, 0.92 MB/s at today's
0.781 s (2.0 MB/s at the modelled 0.36 s); bf16-hopper 704 KiB, 1.08 MB/s (3.6 at 0.20 s); fp8-hopper 622 KiB, 1.79 MB/s (5.9 at 0.11 s);
fp8-ada 622 KiB, 2.53 MB/s (4.0 at 0.16 s); fp4-nvf4 532 KiB, 7.6 MB/s (20 at 0.027 s — the one cell that would exceed 10 MB/s when its
prover is fast; use S = 461 KiB there).  vs today 66–126 MB and 161–262 MB/s: ~100x fewer bytes, 40–100x less egress.  The byte model
reproduces the paper's Table 1 to 0–5 % and proto's eight measured proofs to ≤ 1 %.

**Prover cost relative to today (fp8-ada 4090, B; three buckets, §3.6)**: encode x1.09 in butterflies (3.15e10 vs 2.9e10; the tall-axis
NTT is 2^25 long at rate 3/8), Merkle x0.87 in hashed bytes (10.3 vs 11.9 GB), tests → sumcheck x2.4 in base-mult-equivalents with the
level-1 codeword kept (1.3e11 vs 5.3e10) or x6.0 with the openings recomputed (needed on 24 GB cards), serialization x0.01.  Modelled
total 0.16 s vs today's 0.252 s; 0.25–0.4 s if the zero-check runs at today's memory-bound rate.  Proto's measured PCS-only 0.37 s at
2^29 is 0.24 s of host bookkeeping + fp64 GEMMs on top of encode/Merkle buckets that match the model to 15 %.  Point S costs encode
x2.6 for -83 KiB — not recommended.

**Verifier**: ~0.96 M BabyBear^6 multiplications + 14 k BLAKE3 → 47 ms single-thread Rust (102 ms bf16), 622 KiB read; dominated by the
`(T + |S_L|) x tall_L` final-vector checks (halvable).  Today's verifier re-encodes 197 columns x 3769 rows per sub-batch from 66 MB.

**Interactive rounds**: 51–53 coins per batch at 2 sumcheck variables per coin (90 unpacked, 37 at 3 per coin) = 1.5 s of round trips at
30 ms RTT against a 0.16 s prover → depth 9–11 in flight to hide it; each in-flight batch holds 4.3 GB (message + Merkle leaves), the
4090 fits 5 → 0.35 s/batch (1.7–2.2x slower than compute-bound), the H100 80 GB fits 9 → compute-bound.  Same-DC verifier (1 ms) makes
it depth 2.  FS for the sumcheck rounds only would cut it to 10 live coins but costs `Q . 66 . 3/|F| = 2^-114` at Q = 2^64 in the RO model
with the degree-6 extension — not free.

**ZK in three sentences**: (1) a uniformly random mask column in the top level-1 PCS column (relation rows 4032–4095 = padding) makes
the level-1 fold `v_1` uniform, so every later message (levels ≥ 2 sumchecks, opened rows, final vector, evaluation claims) is a
function of a uniform vector and public coins; (2) 239 consecutive random coefficients per level-1 column (in pad sub-batch cells the
zero-check excludes via a public `act(c)` indicator) make the opened level-1 symbols uniform (scaled Vandermonde), plus one A-cell per
column for the level-1 partial sumcheck; (3) the zero-check's 3n+1 partial sums are hidden Libra-style with a committed random `g`
(91 ext coefficients) — all under live coins (8c); cost: 0 extra cells, +2.2 KB proof, +0.2 % prover.  Same design as ligerito-zk's.

**Top three risks**: (1) zero-check memory/time at real N (K x C tables 12.9 GB base / 38 GB ext in the sumcheck lane's formulation —
must be chunked; arithmetic bucket 0.06–0.3 s), (2) coin latency on 24 GB cards (depth 9 needed, 5 fit → 1.7–2.2x unless same-DC
verifier or H100), (3) soundness constants transcribed from a garbled PDF + docs.rs + the Table 1 fit — the field term has 25+ bits of
slack, but a list-decoding-style factor on level-1 batching would raise |S_1| ≤ 1.5x (+140 KiB); someone with a clean copy should check
(17) against `soundness()`.

**Phase B (§3.8)**: 86 h total — pcs at real shapes 10, sumcheck 14, zk 10, transcript/live 8, relation glue 10, Rust verifier 20,
red-team 6, integration + Table 2 8; critical path ≈ 38 h.

**Branch**: `lane/ligerito-design` head **760260d** (from e0cf2cd; 10 commits; includes the merge of `lane/ligerito-proto` 7bc2fdd);
`git status --short` **empty**.  Files: `backends/direct/ligerito/{params.py, test_params.py, ref.py, test_ref.py, __init__.py}` (+ proto's).
Tests: `python -m pytest backends/direct/ligerito/test_params.py backends/direct/ligerito/test_ref.py` — 42 passed, 20 s, numpy only
(blake3 wheel installed in the lane venv, 1 MB).  Nothing under `backends/direct/ligero/` touched; no .md added to the repo.
