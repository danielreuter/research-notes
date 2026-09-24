---
lane: ligerito-sumcheck-2
created: 2026-09-23T18:45Z
worktree: ~/projects/verity-main-wt/ligerito-sumcheck-2 (branch lane/ligerito-sumcheck-2 from lane/ligerito-sumcheck @ 5b33e23)
pods: vy-ligerito-sumcheck-2 (RTX 4090 reference part, ECC on -> 23028 MiB, b3jhv35qohqtpu, created 18:44Z, $0.74/h)
---

# ligerito-sumcheck-2 — coins, 4090 fit, kernel floor for the Ligerito constraint layer

CHECKPOINT 1fbbe86 (21:03Z) — kernel floor: 4090 0.159 s warm / H100 0.159 s warm (same-session predecessor on the H100:
0.2995 s, 37.07 GB); gate green at 1fbbe86 on the 4090 (20/20 + 3 negatives × 3 modes). H100 terminated 21:00Z.

CHECKPOINT 91a9509 (20:40Z) — LGSC0003 landed: data-driven round schedule (2–3 variables per coin), rows + shift batched
into ONE combined sumcheck, zero-check opening binds 3 variables straight from z (no A/B/C base tables), final zero-check
round sends tables. fp8-ada 4096 VUs on the 4090: 0.408 s warm, peak 14.6 GB, 18 coins (was 62), 11,069 B; 20/20 tests
(CUDA engine byte-identical to the torch reference on 3 schedules) + 3 real-N negatives × 3 cheat modes all rejected.

## Interface (LGSC0003, posted 20:40Z) — `backends/direct/ligerito/sumcheck.py`

Python API (unchanged signatures, additive only): `prove(lay, cons, z, coins, cheat=None, engine=None, schedule=None) ->
SumcheckProof`, `verify(lay, cons, pub_rows, proof, coins, device="cpu") -> (ok, reason, claims)`, `SumcheckProof.to_bytes()`
/ `from_bytes(b, device)`, `.claims` (list of `EvalClaim(point (n_i + n_c, 6) = (p_i || p_c), value (6,), name)`: `1 + n_links`
claims, same order and point convention as LGSC0002), `.timings`. `cheat` ∈ {None, "round1", "zc", "all"} ("zc" is new: every
zero-check message + the final tables fixed, caught at "combined round 0"). `schedule=None` = `default_schedule(n_k + n_c,
max(n_i, n_c))`. `layout.fill_z(sys, lay, z, s, sb)` (new: `build_z` one sub-batch at a time).

Notation: ext element = 6 × u32 LE (coefficients of x^0..x^5 in F_p[x]/(x^6 − 31)), 24 B. A round of arity v binds the v
TOP remaining variables with one coin `challenge(label, v)`; `r[j]` ↔ `X_{j+1}`, `X_1` = the highest remaining variable. Its
message is `M[a_1]..[a_v]` (3^v ext elements, row-major, `a_j ∈ {0, 1, ∞}` = value at X_j = 0, value at X_j = 1, X_j² coefficient),
and `q(r) = Σ_a M[a] Π_j w(a_j, r_j)` with `w(0,r) = 1 − r`, `w(1,r) = r`, `w(∞,r) = r(r − 1)`.

Wire format:
~~~
"LGSC0003"                                    8 B magic
u8 Z, u8 zc_arity[Z]                          zero-check message rounds (first = opening; default 3,2,2,2,2,3,3,3,3,3)
u8 vf                                         variables of the final zero-check round (default 4)
u8 n_links                                    (3 for fp8-ada)
u8 Q, u8 cmb_arity[Q]                         combined rounds (default 3 × 6)
u8 n_values                                   1 + n_links
zc_rounds[t]    3^{zc_arity[t]} ext           t = 0..Z-1
final_abc       3 × 2^vf ext                  Az, Bz, Cz on the last vf variables (index bit t = variable t)
final_next      n_links × 2^vf ext            next_x(r_c_hi, b) for b in {0,1}^vf
cmb_rounds[t]   3^{cmb_arity[t]} ext
values          (1 + n_links) ext             w~(r_i, r_c), then w~(bits(c_x), rho_c) for x = 0..n_links-1
~~~
Bytes: 8 + 1 + Z + 1 + 1 + 1 + Q + 1 + 24 · (Σ 3^zc + (3 + n_links) 2^vf + Σ 3^cmb + 1 + n_links). fp8-ada real N: 11,069 B.
Parser: arities must be in 1..4 and sum to n_k + n_c (zero-check, including vf ≤ n_c) and max(n_i, n_c) (combined); no
trailing bytes; every coordinate < p.

Coins call order (labels are bytes; the header is absorbed first, every message absorbed before its coin):
~~~
absorb  "lgsc/header"  header bytes (magic .. n_values)
tau   = challenge("zc/tau", n)                    n = n_k + n_c; tau[t] <-> variable t of x = k*C + c (k = the high n_k bits)
for t in 0..Z-1:  absorb "zc/q/{t}" M_t;  r = challenge("zc/r/{t}", zc_arity[t])
absorb "zc/final"  final_abc || final_next       (as one (3 + n_links) × 2^vf × 6 array)
ch    = challenge("zc/final", vf + 3)             r_f = ch[0..vf-1] (r_f[j] <-> X_{j+1} = variable vf-1-j), gamma = ch[vf], g3 = ch[vf+1], beta = ch[vf+2]
for t in 0..Q-1:  absorb "cmb/q/{t}" M_t;  r = challenge("cmb/r/{t}", cmb_arity[t])
absorb "values" values
~~~
Coins per batch = 1 + Z + 1 + Q (default 18). Assemble points: `r_var` = all zero-check challenges in bind order, reversed
(r_var[t] ↔ variable t); `r_c = r_var[:n_c]`, `r_k = r_var[n_c:]`; `rho` = all combined challenges reversed; `r_i = rho[:n_i]`,
`rho_c = rho[:n_c]`.

Verifier checks:
1. Zero-check, E = 1, claim = 0, nrem = n. Round t (arity v): taus = tau[nrem−1−j] for j < v; check
   `E · Σ_{b∈{0,1}^v} Π_j eq(tau_j, b_j) M_t[b] == claim` (the ∞ entries have weight 0); then `E *= Π_j eq(tau_j, r_j)`,
   `claim = E · q_t(r)`, nrem −= v.
2. Final: `E · Σ_b eq(tau[:vf], b) (abc0·abc1 − abc2)[b] == claim` (tables indexed by b with bit t = variable t, eq table
   bit t ↔ tau[t]). Then `A = Σ_b eq(r_var[:vf], b) abc0[b]` etc., `next_x = Σ_b eq(r_var[:vf], b) final_next[x][b]`.
3. Combined initial claim `beta · 2^(n_cmb − n_i) · (A + gamma B + gamma² C) + 2^(n_cmb − n_c) · Σ_x g3^x next_x`;
   each round `Σ_{b∈{0,1}^v} M_t[b] == claim`, then `claim = q_t(r)`.
4. Final: `beta · coef(r_i) · z(r_i, r_c) + succ(rho_c, r_c) · Σ_x g3^x values[1+x] == claim`, with
   `coef = eq(r_k, ·)^T (A + gamma B + gamma² C)` (the verifier's O(nnz)), `z(r_i, r_c) = values[0] + Σ_{public virtual rows v}
   eq(r_i, idx_v) pub_v~(r_c) + Σ_x eq(r_i, idx(next:x)) next_x`, `succ` = the closed form (`succ_mle`, unchanged from LGSC0002).
5. PCS: `w~(r_i || r_c) = values[0]`, `w~(bits(c_x) || rho_c) = values[1+x]` (unchanged from LGSC0002).

Fixture: `~/.research/notes/lanes/ligerito-sumcheck-2/evidence/lgsc0003_fixture_fp8-ada_l64_S2.json.gz` (112 KB; sha256
6de82f6b…d6c7; `python -m backends.direct.ligerito.sumcheck --fixture PATH` regenerates it). JSON keys: `format`, `schedule`,
`coin_count` (11 at the toy size), `layout` (incl. `virt`, `c_rows`, `n_j`), `constraints` (`K_pad`, COO `a/b/c` = [k[], row[],
coef[]]), `public_rows`, `proof_hex`, `claims`, `transcript` (every absorb (hex) and every challenge (values) in order, with
`LocalCoins(b"fixture")`), `negatives` (4 byte flips + a "zc" and an "all" cheat on a violated witness: each must be rejected,
with the Python reason).

## 1. Coins: 62 → 18 per batch (sumchecks alone)

Baseline measured, not taken from the report: the LGSC0002 prover draws `n + n_i + n_c + 2` coins (tau, the bivariate opening,
n − 2 univariate zero-check rounds, gamma, n_i rows rounds, the shift's g3, n_c shift rounds) — 40 at the toy size (measured on
the pod, labels counted) and **62** at fp8-ada 4096 VUs (n = 30, n_i = 12, n_c = 18; the predecessor's report says 61).

What changed, in order of coins saved:
* **Rows + shift → one combined sumcheck** over `y` (max(n_i, n_c) = 18 variables): `h(y) = beta coef(y_lo) z~(y_lo, r_c) +
  succ~(r_c, y) V(y)`; rows on the low 12 variables (tiled 2^6 times), shift on all 18. The shift's claim point moved from
  its own challenge to the shared `rho`. −12 coins.
* **2–3 variables per coin**: zero-check 3 (opening) + 2,2,2,2 (while the tables are > 2^20 cells: bivariate keeps the O(N)
  kernels in registers) + 3,3,3,3,3; combined 3 × 6. −26 coins.
* **Final table round**: the last vf = 4 zero-check variables are sent as tables (3 × 16 values + the next rows' 3 × 16) and
  bound by the same coin that draws gamma, g3, beta. −4 coins (gamma, g3 and the last rounds merge).
* Zero-check opening ↔ PCS first rounds: **cannot share**. The PCS's first coins are its round-1 column-sumcheck challenges, and
  that sumcheck needs the evaluation point, which exists only after our last coin. What CAN merge (not done: needs
  ligerito-proto's round-1 sumcheck to accept a non-eq row weight): our rows part `Σ_i coef(i) w~(i, r_c)` and the PCS
  round-1 sumcheck `Σ_i eq(r_i, i) u(i)` with `u(i) = w~(i, r_c)` are sumchecks over the same 12 row variables of the same
  table (row-major commit, x = c + C i). Running the PCS's round 1 with weight `coef` instead of `eq` makes the rows claim the
  PCS's own starting point: another ~12 coins saved per batch, and one claim fewer. Listed for ligerito-relation / -proto.
* tau is the first coin after the commitment; if the relation draws any other challenge between commit and tau, both come from
  one coin.

Soundness (|F| = p^6, p = 2013265921, log2 |F| = 185.44). A round with arity v sends a polynomial of degree ≤ 2 per
variable, so a false message agrees with the true one at the random point with probability ≤ 2v/|F| (Schwartz–Zippel,
total degree 2v; the zero-check's eq factor is the verifier's own). Per round: v = 1: 2^-184.4, v = 2: 2^-183.4, v = 3:
2^-182.9 (the per-round error grows linearly in v; the round count falls by v, so the sum is unchanged):
~~~
zero-check tau reduction          n/|F|          = 30/|F|
zero-check message rounds         2*26/|F|       = 52/|F|      (3 + 2*4 + 3*5 = 26 variables)
final tables at r_f               vf/|F|         =  4/|F|
batching gamma (deg 2), g3 (deg n_links-1 = 2), beta (deg 1)      =  5/|F|
combined rounds                   2*18/|F|       = 36/|F|
total                             127/|F| = 2^(6.99 - 185.44) = 2^-178.4
LGSC0002 for comparison           (30 + 60 + 2 + 24 + 2 + 36)/|F| = 154/|F| = 2^-178.2
~~~
Both leave ≥ 50 bits of the 2^-128 budget. Interactive (live-coin) soundness, which is what one coin = one round trip
means. Under Fiat–Shamir, state-restoration soundness is ≈ Q · max per-round error = Q · 6/|F|: Q ≤ 2^54 hash queries stays
under 2^-128 (v = 1 would allow 2^55): arity 3 costs 1.6 bits of that margin.

## 2. 4090 fit: 37.1 GB → 14.6 GB peak (full 4096-VU batch)

The 37.1 GB came from the three base tables Az, Bz, Cz (3 × 2^30 × 4 B = 12.9 GB) plus the first fold into the extension
(3 × 2^29 × 24 B = 38.7 GB, halved in place). Now:
* the **opening round binds the top 3 constraint-slot bits straight from z** through the CSR matrices (`zc_open3_msg`: one block
  per (k', a_1) pair, 9 message entries per thread, the column eq weight per cell and the row weight once per block;
  `zc_open3_fold`: the 8-way fold gathered from z): no base tables; the first extension table is 3 × 2^27 × 24 B = 9.66 GB;
* every later fold is in place;
* `bench` builds z one sub-batch at a time (`layout.fill_z`) and drops each witness.
Peak = z (4.29 GB) + the 9.66 GB table + small tables: **14.45 GB allocated, 14.60 GB reserved** at 1fbbe86 of the 4090's
22.0 GB usable (ECC on). Half batches not needed (they would have cost a second PCS proof, ~+690 KB, and a second set of ~18 + ~21 coins
unless the two halves share coins).

## 3. Kernel floor: 0.291 s (H100) → 0.159 s on BOTH the 4090 and the H100

fp8-ada 4096 VUs (N = 2^30 zero-check cells), `python -m backends.direct.ligerito.sumcheck --vus 4096 --engine cuda --reps 4
--negatives`, LocalCoins, warm (allocator cache warm; first run in a process 0.31 s = cupy module load + 9.7 GB first mapping):

| | 4090 @ 1fbbe86 | H100 @ 1fbbe86 | predecessor 5b33e23, same H100 session |
|---|---|---|---|
| prove total | **0.159 s** | **0.159 s** | 0.2995 s |
| peak allocated / reserved | 14.45 / 14.60 GB | 14.45 / 14.60 GB | 37.07 GB |
| coins | 18 | 18 | 62 |
| message bytes | 11,069 | 11,069 | 4,645 |
| verify (Python, on device) | 1.2 s | 0.93 s | — |

Breakdown on the 4090 (ms): opening round 75 (message 57 from z + 8-way fold from z 18) · round 2, bivariate over 2^27 ext
cells 35 (message 19 + fold 16) · round 3 10 · rounds 4–10 ~1.2 each · final tables 1 · coef on device + z(·, r_c) matvec
+ eq tables 14.5 · combined setup 4.4 · combined 6 rounds 3.9 · values ~3. The H100 isn't faster because these kernels are
integer-multiply bound (Montgomery products in F_{p^6}), not bandwidth bound; the 4090's higher clock evens out HBM.

What did it (each step byte-identical to the torch reference; `test_cuda_engine_matches_reference` × 3 schedules):
1. trivariate opening straight from z (no base tables: −12.9 GB, and the 38.7 GB first extension table became 9.7 GB);
2. `coef = eq(r_k)^T(A + γB + γ²C)` as one scatter kernel `sc_coef` (was 22–29 ms in torch; now inside the 14.5 ms bucket);
3. small rounds reduced in-kernel (`zc_red{1,2,3}`, `pp_red{1,2,3}`: grid (x, 3^v), block reduction + atomics) instead of
   writing 3^v × groups entries and summing in torch (−~50 ms);
4. the eq weight planes built lazily on the device per size needed (was 77 ms of torch prefix tables) and each round's
   2^v corner weights computed on the host in pure Python (was ~7 ms/round of tiny torch launches);
5. stripe-major grids for the opening kernels (consecutive blocks share a column stripe of z in L2) and the opening
   message's 54 accumulators in shared memory (216 → 80 registers; 75 → 57 ms);
6. `red39` (two folds by 2^32 mod p) instead of `u64 % p` in the extension product; 8-row matvec blocks;
7. the bench no longer empties the CUDA cache between proofs (re-mapping 9.7 GB cost ~50 ms per proof).
Not done: fused fold + next-message kernels. The O(N) rounds are compute bound (msg2 is 19 ext products per 4-cell group),
so fusing would only save the re-read of the folded table (≤ ~10 ms). Karatsuba-style ext products (36 → ~24 Montgomery
multiplies) would help every O(N) kernel by an estimated 20–30%. Tried and dropped: CSR staged in shared memory (slower);
columns per thread 4 / 8 / 16 (no change).

## 4. For ligerito-relation

* Pull `lane/ligerito-sumcheck-2` @ 1fbbe86 (branches from `lane/ligerito-sumcheck` @ 5b33e23; touches only `layout.py`
  (+`fill_z`), `sumcheck.py`, `sumcheck_test.py`). Your call sites are unchanged (checked against `lane/ligerito-relation`
  `prove.py`): `prove(lay, cons, z, coins, cheat=, engine=)`, `verify`, `SumcheckProof.to_bytes/from_bytes`, `.claims`,
  `_marshal_pad`. `.timings` keys changed (`zc`, `zc_rounds`, `zc_msg`, `cmb*`, `total`); your
  `k != "sumcheck1_rounds"` filter is harmless.
* Item 0 of your 19:55Z handoff is in: only rows `[m, m + len(virt))` are zeroed in `w`.
* Cheat modes: "round1" → "zero-check round 1", "zc" (new) → "combined round 0", "all" → "combined final"; an honest proof
  on a violated witness → "zero-check round 0". Update any negative that matches on the old strings ("round 2", "row
  sumcheck final", "shift …").
* Memory: at 4096 VUs the prover needs z (4.3 GB) + 10.2 GB. If you prove on a 4090, keep your other device buffers
  ≤ ~7 GB during `sumcheck.prove`, and set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` if the torch verifier runs in
  the same process between proofs (fragmentation OOM otherwise). If you build z yourself, `layout.fill_z` per sub-batch
  avoids holding all 16 witnesses.
* PCS: the same `1 + n_links` claims as before, same points. Coin total per batch ≈ 18 + PCS ~21 = 39 (design budget 51–53).
  Merging our rows part into the PCS's round-1 sumcheck saves ~12 more coins (§1); that needs ligerito-proto's round 1 to
  take a row weight vector instead of `eq(r_i)`.
* ZK (your items 1–3) and fp4 component ends: see my 20:45Z reply in your notes. Not from this lane; fp4 is yours to land
  in `fill_z` / `constraints`.

## 5. For ligerito-verify-rs

* New format **LGSC0003**, spec in `## Interface` above; fixture
  `~/.research/notes/lanes/ligerito-sumcheck-2/evidence/lgsc0003_fixture_fp8-ada_l64_S2.json.gz` (regenerated at 1fbbe86:
  identical JSON, sha256 of the JSON 019869b0…534b). It includes the full transcript (absorbs + challenges in order) so you can
  check your Coins calls step by step, and 6 negatives.
* What changes vs LGSC0002 for a verifier: (1) round messages are `3^v` entries in the `{0, 1, ∞}` mixed representation,
  one coin per round with `v` challenges (`r[j]` ↔ `X_{j+1}` = the TOP remaining variable, i.e. the zero-check still binds
  from the top: k bits first, then c bits); (2) the zero-check's last `vf` variables come as tables and one coin draws
  `r_f`, gamma, g3, beta; (3) rows + shift are ONE combined sumcheck over `max(n_i, n_c)` variables with initial claim
  `beta 2^(n_cmb−n_i) rows + 2^(n_cmb−n_c) shift` and final check `beta coef(r_i) z(r_i, r_c) + succ(rho_c, r_c) V(rho_c)`;
  (4) `next_vals` are no longer sent. They are the tables' MLE at `r_f`; (5) the arities come from the header, so accept any
  1..4 that add up.
* Helpers you need beyond LGSC0002: `eval_mixed` (contract each axis with `(1 − r, r, r(r − 1))`), `eq_sum_mixed` (`(1 − τ, τ, 0)`),
  `bool_sum_mixed` (`(1, 1, 0)`). Contract axis 0 (X_1) first; the order doesn't change the value.

## FINAL (21:06Z)

* Branch `lane/ligerito-sumcheck-2` head **1fbbe86262da02bbcede0deefb0961df360eed53**; `git status --short` empty.
* **Coins/batch (sumchecks) 62 → 18** (measured by counting Coins calls; the predecessor reported 61). Soundness: per-round
  2v/|F| (v = 1: 2^-184.4 … v = 3: 2^-182.9), total 127/|F| = **2^-178.4** (LGSC0002: 154/|F| = 2^-178.2); ≥ 50 bits
  inside 2^-128. Under Fiat–Shamir, state-restoration costs 1.6 bits vs univariate rounds (Q ≤ 2^54). Zero-check opening ↔ PCS
  first rounds can't share coins (the PCS needs the evaluation point); rows ↔ PCS round 1 could (~−12 more), cross-lane.
* **4090 (reference part, ECC on, 22.0 GB usable), full 4096-VU batch: 0.159 s warm, peak 14.45 GB allocated / 14.60 GB
  reserved.** No half batches.
* **H100 80 GB: 0.159 s** warm, same peak (predecessor, same session: 0.2995 s, 37.07 GB).
* Message: 11,069 B (LGSC0002: 4,645 B; +6.4 KB per ~0.7 MB proof).
* Format **LGSC0003**; fixture `evidence/lgsc0003_fixture_fp8-ada_l64_S2.json.gz` (112 KB).
* Tests: `sumcheck_test.py` 20/20 on the 4090 and the H100. The 11 previous tests are all kept; roundtrip is now
  parametrized over 5 schedules and the CUDA-vs-reference byte check over 3, plus schedule/coin, truncation and CUDA-helper
  tests. Real-N negatives (quadratic, chain link, lookup) × (honest, "zc", "all") all rejected at 4096 VUs on the 4090 @
  1fbbe86 and on the H100. Evidence JSONs in `evidence/`.
* Pods: H100 `xnbxeyz0kyfsig` 20:50–21:00Z, ~$0.45, terminated. 4090 `b3jhv35qohqtpu` 18:44Z–21:05Z, ~2.35 h × $0.74 ≈ $1.74,
  terminated at FINAL. Total ≈ $2.20 of $8.
* Remaining: (1) ZK hooks in the mixed-round format (EqSumcheckMask per mixed entry, masked combined sumcheck, shift-claim
  reduction, 4 committed ZK rows); (2) fp4 component ends in `layout.py` (ligerito-relation lands it); (3) rows ↔ PCS round-1
  merge (−12 coins, with ligerito-proto); (4) Karatsuba ext product / fused fold + message (est. −20–30 ms); (5) Rust
  verifier update to LGSC0003 (ligerito-verify-rs); (6) bf16 relation not measured (instance index fixture not in git).
