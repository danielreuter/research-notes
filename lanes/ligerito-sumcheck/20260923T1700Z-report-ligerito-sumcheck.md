---
lane: ligerito-sumcheck
kind: report
created: 2026-09-23T17:00Z
status: final
---

CHECKPOINT 5b33e23 (18:40Z) **FINAL** — `git status --short` empty on `lane/ligerito-sumcheck` (7 commits over e0cf2cd, all in `backends/direct/ligerito/{__init__,layout,sumcheck,sumcheck_test}.py`). 11 tests pass on the pod (CPU reference path + CUDA byte-parity). **fp8-ada 4096 VUs, H100, steady state: 0.291 s per batch (zero-check 0.220, rows 0.038, shift 0.010, tables 0.023) = 1.4× today's `t.arithmetic` 0.209 s; 37.1 GB peak; 4645 B; 61 coins; three negatives reject (round 0 for the honest-on-bad-witness prover, the final claim for the round-fixing prover).** bf16-hopper 4096 VUs (N = 2^31): 0.482 s, 73.6 GB. fp8-ada 2048 VUs: 0.190 s, 18.6 GB (the 4090-sized batch). Chain shift = shifted virtual rows + one degree-2 sumcheck over the column variables (§1, §4): 10 ms, 3 claims, 18 × 72 B. Interface §3 (LGSC0002, posted 18:20Z, opening bivariate round added 18:35Z), fixture for ligerito-verify-rs in `evidence/`. Pod `k8ixstiy66e1lx` (H100 80GB, $3.49/h by the API — the machines.toml comment says $2.69) created 17:42Z, terminated 18:39Z: ≈ $3.3 of the $8 cap. Still needed for integration: §5.

CHECKPOINT 835c97a (18:20Z) — `layout.py` + `sumcheck.py` (+ `sumcheck_test.py`, 11 tests incl. 4 negatives and a CUDA-vs-reference byte-equality test) run on the pod (`vy-ligerito-sumcheck`, H100 80GB HBM3, pod k8ixstiy66e1lx, created 17:42Z). **Measured at real N (fp8-ada, 4096 VUs, 13 real sub-batches padded to S = 16, N = 2^30, tables 3 × 2^30):** zero-check 0.472 s (rounds: 66, 104, 54, 30, 18, 12, 9, 7, 6, 6, 6, 6 ms, then 18 column rounds at 5.5 ms each), rows sumcheck 0.205 s, shift sumcheck 0.115 s, table build 0.242 s → **1.03 s per batch vs t.arithmetic 0.209 s (4.9×)**; peak 56.4 GB device memory; messages **4573 B**; Python verifier 0.71 s; the three negatives (violated quadratic row / chain link / lookup) all reject: the honest prover on the bad witness fails round 0, the prover that fixes every round's `q(1)` reaches the end and fails the final claim. §2 has the numbers, §3 the Interface (posted 18:20Z, ahead of 20:30Z). Read ligerito-design's 17:55Z note and ligerito-proto's 17:45Z interface: adopted their Coins surface (`bytes` labels, `absorb` every message, `np.ndarray (n, 6)` challenges) and their column-major PCS index (`x = row + R · col`) for the claim points (§4). Next: shave the fixed 5.5 ms/round floor (prover-side bookkeeping, not the kernel), bf16-hopper at the size that fits, then FINAL.

CHECKPOINT none (17:20Z) — briefs + compile.py / PROTOCOL.md / protocol.py / chain.py / witness.py / relchain.py read; worktree `~/projects/verity-main-wt/ligerito-sumcheck` on `lane/ligerito-sumcheck` from e0cf2cd; design fixed (§1 below); counts measured on the laptop (fp8-ada: 3532 quadratic + 589 linear (192 of them `pin:` rows) + 3 links; bf16-hopper 3164 + 339 (96 pins)); no pod yet (code first).

# ligerito-sumcheck — `compile.System` → multilinear layout → batched degree-3 zero-check → evaluation claims

## 1. Design (fixed 17:20Z; the measured numbers decide what stays)

**Committed polynomial.** One multilinear `w̃` per batch over `N = 2^(n_i + n_s + n_j)` cells = the MLE of the `R × C` table
`z[i, c]` (`i` = row, `c = s·l + j`, `s` = sub-batch, `j` = column within the sub-batch).  Claim points are given in ligerito-proto's
PCS variable order (18:20Z: `x = i + R·c`, the row bits are the LOW `n_i` variables, then the `n_c` column bits; LSB first,
`eq(r, x) = Π_t (r_t x_t + (1 − r_t)(1 − x_t))`) — the MLE value does not depend on which block is high, only the point's
coordinate order does.  fp8-ada at 4096 VUs: `l = 16384` (`n_j = 14`), 12 real sub-batches
padded to `S = 16` (`n_s = 4`; pad sub-batches are trivial-unit VUs with `y16 = 0`, exactly Ligero's pad units), rows padded to
`2^12` (`n_i = 12`) → `N = 2^30`.  Rows `i < m'` are the System's rows MINUS the `pin` rows (see next); rows `[m', 4096)` are ZERO in
the commitment and are where the prover's *virtual rows* live.

**Pins become public rows.** A `pin` row is constrained `W_row = pub(j)` and used with scalar coefficients elsewhere; in a sumcheck the
public per-column vector can be referenced directly, so pins are not committed and their 192 `pin:` linear constraints vanish.  This is
what makes fp8-ada fit `2^12` constraint slots (3532 + 397 + 7 chain = 3936 ≤ 4096; with the pin rows it would be 4128 → 13 bits, 2×
the tables) and `2^12` rows (3577 committed + 192 pub + 3 shifted + 4 masks + 1 const = 3777 ≤ 4096).

**Column vector `z_j`** (what every constraint is affine in) = `[committed rows | virtual rows]`, virtual = the pub rows (Ligero's
`pub` vectors incl. the former pins), the constant-1 row, the chain masks `link/start/end` (0/1 per column, a function of the
layout), `y16_pub`, and the `n_links` SHIFTED rows `Wnext_x(s, j) = W(c_x, s, j + 1 mod l)`.  Every constraint is then uniform
`A_k(z) · B_k(z) = C_k(z)` with scalar coefficients: `Quadratic` as is; `Linear` `L(W) + c = pub` as `A = L + c − pub_row, B = 1, C = 0`;
chain link `A = link_row, B = Wnext_x − Y_x(W), C = 0`; start `A = start_row, B = W_{c_x}`; end `A = end_row, B = Y16(W) − y16_row`;
lookups / range bits are already `Quadratic`/`Linear` rows (one-hot, key selection, booleanity) — nothing special.  `System.wide` is
only a hint-partition record (no constraint of its own): nothing to do.

**Sumcheck 1 — the zero-check** over `(k, c)`, `k` = constraint slot (`n_k = 12`), `c = (s, j)` (`n_s + n_j = 18`): 
`Σ_{k,c} eq(τ, (k, c)) · (Az·Bz − Cz)(k, c) = 0` with `Az = A z` etc. (tables `K × C`, base field, built by sparse gathers from `z`).
Gruen's factorisation: the round polynomial is `eq(τ_t, X) · q(X)` with `q` quadratic; the prover sends `q(0), q(1), q(∞)` (3 ext),
the verifier checks `(1 − τ_t) q(0) + τ_t q(1) = claim` and continues with `eq(τ_t, r_t) q(r_t)`.  Bind order: the `k` bits (top down)
first, then the `c` bits — so the tables shrink along the contiguous row axis and the `eq` weight is always a tensor product
`eq_rows ⊗ eq_cols` (never a `2^30` table).  Ends in claims `Az(r), Bz(r), Cz(r)`.
**Sumcheck 2 — rows** (`n_i = 12`, degree 2): `Az(r_k, r_c) = Σ_i α(i) z̃(i, r_c)` with `α = eq(r_k, ·)ᵀ A` (verifier-computable,
`nnz(A)` ext ops), batched over the three tables by `γ`: `Σ_i (α + γβ + γ²ζ)(i) z̃(i, r_c)`.  The prover's table `z̃(·, r_c) = z · eq_c`
(one `4096 × 2^18` matvec, base × ext).  Ends in `z̃(r_i, r_c) = w̃(r_i, r_c) + Σ_v eq(r_i, idx_v) · virt_v(r_c)`: the first term is
THE evaluation claim on the committed polynomial; the virtual terms are the verifier's (`pub` MLEs at `r_c`, const = 1, masks) except
the shifted rows, whose values `Wnext_x(r_c)` the prover claims and proves by
**Sumcheck 3 — the shift** (`n_c = 18`, degree 2): `Σ_x γ^x Wnext_x(r_c) = Σ_c succ̃(r_c, c) · V(c)`, `V(c) = Σ_x γ^x W(c_x, c)`,
`succ̃(r, c) = eq(r, pred(c))` (the eq table rolled by one along `j`, cyclic in the sub-batch; the wrap position is never a link).
Ends in `succ̃(r_c, ρ) · Σ_x γ^x w̃(bits(c_x), ρ)`: `n_links` more point-evaluation claims on `w̃` at `(bits(c_x), ρ)`, and the verifier
evaluates `succ̃(r_c, ρ)` — the MLE of the cyclic successor relation — in `O(n_j²)` (closed form, checked against brute force).
This is the "shifted-polynomial identity"; the "sparse-matrix sumcheck" for the same links has the SAME prover work (the sparse
matrix is the shift, its `Ã(r, ·)` is the rolled eq table) and an `O(l)` verifier evaluation instead of `O(log² l)` — both are
implemented as verifier paths and cross-checked; the prover time is one number.

**Output.** `1 + n_links` evaluation claims `(point ∈ F^30, value ∈ F_{p^6})` on `w̃` for the PCS to batch (ligerito-proto's tensor
claims batch by `α`; four claims cost nothing there).  Messages ≈ `(30 + 12 + 18) × 3 × 24 B + 3 + 3 claims ≈ 4.5 KB` per batch.
Soundness: `Σ rounds · degree / |F|` ≈ `(30·3 + 12·2 + 18·2 + 30 + 4) / 2^186 < 2^-178`.

**Field.** `F_{p^6} = F_p[X]/(X^6 − 31)` — `backends/direct/ligero/v2/fc.py` (torch int64, 6 coords on the last axis), the same
tower ligerito-proto chose.  Coins: `transcript.Coins.challenge(label, n) -> (n, 6)` (ligerito-proto's protocol; a local deterministic
stub with that signature until theirs lands).

## 2. Measured (pod H100 80GB, `python -m backends.direct.ligerito.sumcheck --relation fp8-ada --vus 4096 --S 16 --engine cuda --negatives`; JSON in `evidence/`)

fp8-ada, 4096 VUs: `l = 16384`, 13 real sub-batches (341 VUs each; 4096 / 341 = 12.01 so 13, not 12) padded to `S = 16`; `m = 3577`
committed rows + 200 virtual rows (192 pub incl. the former pins, const, link/start/end, y16, 3 shifted) in `R = 2^12`; `K = 3936`
constraints in `2^12` slots (`nnz(A, B, C) = 10623 / 5337 / 3498`); `C = 2^18`, `N = 2^30`; witnesses from the Ligero code
(`relchain.marshal` + `rel.hints` + `witness.build_witness`; 7 s for 4096 VUs, outside the prover's clock).  bf16-hopper at 2048 VUs
(`steps = 96`, 13 × 170 VUs, the same `N = 2^30`): `m = 3196`, `K = 3414`, identical timings to the ms — the cost is `N`, not the
relation; its 4096-VU batch is `N = 2^31` (2× everything below, ~73 GB peak).

**Final code (5b33e23): fp8-ada 4096 VUs, one batch, H100, steady state** (the bench proves twice; the first prove in a process
pays ~75 ms of cupy import + kernel-cache load: 0.365 s cold)

| stage | s | notes |
|---|---|---|
| tables `Az, Bz, Cz` (3 × 2^30 int32) | 0.023 | one CSR gather kernel per side from `z` (4.3 GB) |
| zero-check, 29 messages | **0.220** | opening bivariate round (base, two variables, 2^28 quads → 3 × 2^28 ext cells) 65 ms; then 49, 25, 13, 6.5, 3.5, 2, 1.2, 0.9, 0.6, 0.4 ms (ext rounds, volume halves each time); 18 column rounds ≈ 0.3 ms each |
| rows sumcheck (12 rounds) | 0.038 | `coef = eq(r_k)ᵀ(A + γB + γ²C)` 22 ms (torch index_add over nnz — the verifier's computation, done by the prover too), `z̃(·, r_c)` matvec kernel 9 ms, eq table < 1 ms, rounds 4 ms |
| shift sumcheck (18 rounds) | 0.010 | the same round kernels with uniform weights on the `(2^18, 6)` tables |
| **prover total** | **0.291** | vs today's `t.arithmetic` 0.209 s (H100 FP8): **1.4×**; vs 0.129 s on the 4090: 2.3× (if it fit — see below) |
| peak device memory | **37.1 GB** | `z` 4.3 + base tables 12.9 + ext planes after the opening fold 19.3 (int32 planes, in-place folds afterwards) |
| message bytes | **4645** | 13 B header + 193 ext elements × 24 B (9 + 27·3 + 3 + 12·3 + 3 + 18·3 + 4) |
| coins | 61 | sequential verifier messages (tau, r01, 27 r's, γ, 12 r's, γ3, 18 r's) |
| Python verifier | 0.77 s | `coef` + the 192 public-row MLEs at `r_c` (192 × 2^18 base × ext, torch limb GEMM) dominate; a Rust verifier is ≈ 10 ms of field ops |

Other sizes, same code (steady state): **bf16-hopper 4096 VUs** (`steps = 96`, 25 × 170 VUs → `S = 32`, `C = 2^19`, `N = 2^31`):
**0.482 s**, peak **73.6 GB** (fits the 80 GB with 6 GB to spare), 4789 B, 62 coins — 2× the fp8 zero-check, as expected.
fp8-ada **2048 VUs** (`S = 8`, `N = 2^29`): **0.190 s**, peak **18.6 GB**, 4501 B; 1024 VUs (`S = 4`): 0.15 s, 9.3 GB.

History of the same run (JSON in `evidence/`): 1.034 s with single-variable rounds, int64 torch tables, torch host bookkeeping
(17:55Z); 0.68 s after Montgomery kernels + precomputed eq prefix tables + no per-round host work; 0.56 s after the bivariate opening
round (56 → 37 GB); 0.36 s cold / 0.29 s warm after moving the rows/shift sumchecks and the eq tables onto the kernels.  Each step was checked byte-identical
against the torch reference path on the toy case (`test_cuda_engine_matches_reference`).

**Negatives (real N, all three cases, both prover behaviours):** violated quadratic row (a `bit` row set to 2), violated chain link
(`c_in` of column 5 bumped; the shifted row kept consistent with the bad committed row), violated lookup (two selectors of the same
lookup on): honest prover on the bad witness → `zero-check round 0: sum_{x1,x2} eq(tau, x) M[x1][x2] != claim`; prover that fixes
every round's `q(1)` (and the opening round's `M[1][1]`) to pass the running check → `zero-check final: eq(τ, r)(Az·Bz − Cz)(r) !=
claim`.  Plus (toy size, CPU): a prover whose shifted row is not the rolled committed row → the shift sumcheck rejects; wrong coins
reject; a prover that fixes only the opening round is caught at round 2; CUDA path byte-identical to the reference path.

**Where the time is and what it means.** After the opening fold every table is in `F_{p^6}`: the zero-check's volume is
`3 × N/4` ext cells read twice and written once per round with 10 ext multiplications per pair (round 1 alone: `2^27` pairs, 49 ms
≈ 1 T Montgomery products/s ≈ 35 % of the H100's int32 peak).  Binding one more variable in the opening round (a trivariate message,
27 ext elements) would halve it again (−~60 ms); fusing fold + next message saves one read per round (−~10 %); the CSR gather can be
a 2-D grid (−~60 ms).  Realistic floor on the H100 ≈ 0.2 s per 4096-VU batch = today's `t.arithmetic`; the commitment side
(encode + Merkle of 2^30 base cells, ligerito-proto/-design's part) comes on top.  **Memory decides the 4090:** 37 GB at 4096 VUs does
not fit 24 GB; 2048-VU batches (`S = 8`, `N = 2^29`) measure 18.6 GB and 0.19 s on the H100 (the zero-check is linear in `N`, the
rest fixed), so the ada cell runs two half-batches per today's batch (2 × 0.19 s on the H100; the 4090 has ~1/3 of the int32 throughput
and 1/3 of the bandwidth, so expect ≈ 0.5 s per half-batch there — 4× today's 0.129 s arithmetic, to be measured) or a column-striped
zero-check that never holds the whole tables (same messages; not written).  That is the open layout decision for the 4090; the H100 numbers stand for fp8-hopper as is.

## 3. Interface (posted 18:20Z; frozen unless ligerito-relation objects by 21:00Z)

Module `backends/direct/ligerito/layout.py`:

~~~
layout_for(sys: compile.System, l: int, n_vus: list[int], steps: int) -> Layout
    Layout: m (committed rows = System rows minus pins), n_i, l, n_j, n_sub, n_s, steps, n_vus, row_of_sys {sys row idx -> committed row},
            virt {name -> row in [m, 2^n_i)}, c_rows (committed rows of sys.chain["c"]), n_k, K; properties S, C = S*l, R = 2^n_i, n_c, n_vars, N, n_links
constraints(sys, lay, device="cpu") -> Constraints          # K_pad = 2^n_k, R, coo {"a"|"b"|"c": (k, row, coef) int64 (nnz,)}, names[k]
SubBatch(W (sys.m, l) int | None, pub {name -> (l,)}, ypub (l,), n_vus)      # .public() drops W (verifier side)
build_z(sys, lay, subs: list[SubBatch] (len S), device, dtype=int32) -> z (R, C) int32   # committed rows, virtual rows, shifted rows
public_rows(sys, lay, subs (public), device) -> {name -> (C,) int64}       # every virtual row except next:* (the verifier's side)
~~~

Module `backends/direct/ligerito/sumcheck.py`:

~~~
prove(lay, cons, z, coins, cheat=None, engine=None|"cuda") -> SumcheckProof        # torch prover; engine="cuda" = fused cupy rounds
verify(lay, cons, pub_rows, proof, coins, device="cpu") -> (ok: bool, reason: str, claims: list[EvalClaim])
SumcheckProof: rounds1 (n_k+n_c, 3, 6)  abc (3, 6)  rounds2 (n_i, 3, 6)  next_vals (n_links, 6)  rounds3 (n_c, 3, 6)  values (1+n_links, 6)
               .to_bytes() / SumcheckProof.from_bytes(b)  .n_bytes()  .claims (derived, not serialised)  .timings
EvalClaim: point (n_i + n_c, 6) ext, value (6,) ext, name       # w~(point) = value on the committed polynomial
ligero_subbatches(rel, runner, vus, l, S, device) -> (subs, n_vus)   # witnesses via the Ligero code (produce only)
bench(relation, n_vus, l, S, device, engine, negatives) -> dict   /  python -m backends.direct.ligerito.sumcheck --help
~~~

**Coins.** Everything random comes from the `coins` object with ligerito-proto's `transcript.py` surface: `absorb(label: bytes,
data: bytes)`, `challenge(label: bytes, n) -> (n, 6)` (numpy or torch, coords in `[0, p)`), `indices`, `rounds`.  Call order (= the
protocol; prover and verifier identical; the caller has already absorbed the PCS commitment):

~~~
challenge(b"zc/tau", n_k + n_c)                                   # tau[t] <-> variable t of (k, c); k = the high n_k bits
absorb(b"zc/q/0", M (3, 3, 6));  challenge(b"zc/r01", 2)          # the OPENING round binds the two top variables (r1 = [0], r2 = [1])
for t in 2 .. n_k + n_c - 1:  absorb(b"zc/q/{t}", q_t (3, 6));  challenge(b"zc/r/{t}", 1)      # binds the top remaining variable
absorb(b"zc/abc", abc (3, 6));  challenge(b"rows/gamma", 1)
for t in 0 .. n_i - 1:        absorb(b"rows/q/{t}", (3, 6));    challenge(b"rows/r/{t}", 1)
absorb(b"rows/next", next_vals (n_links, 6));  challenge(b"shift/gamma", 1)
for t in 0 .. n_c - 1:        absorb(b"shift/q/{t}", (3, 6));   challenge(b"shift/r/{t}", 1)
absorb(b"values", values (1 + n_links, 6))
~~~

Coins: `1 + 1 + (n_k + n_c − 2) + 1 + n_i + 1 + n_c` = 61 sequential verifier messages for fp8-ada.  Absorbed bytes = the wire
form of the named message.  `sumcheck.LocalCoins(seed)` is the diagnostic stub with that surface (ignores absorbs).

**Wire format** (`SumcheckProof.to_bytes`, **4645 B** for fp8-ada and bf16 at any batch size with `n_c = 18`): magic `LGSC0002`
(8 B), then `u8 × 5`: `n1 = n_k + n_c − 2`, `n2 = n_i`, `n3 = n_c`, `n_links`, `n_values = 1 + n_links`; then, each as little-endian
`u32` coordinates (coefficient of `X^i` of `F_p[X]/(X^6 − 31)`, `i = 0..5`, values `< p`, non-canonical values are rejected):
`round0[3][3][6]`, `rounds1[n1][3][6]`, `abc[3][6]`, `rounds2[n2][3][6]`, `next_vals[n_links][6]`, `rounds3[n3][3][6]`,
`values[n_values][6]`.  A univariate round message is `(q(0), q(1), q(∞))` with `q(∞)` = the `X²` coefficient;
`q(r) = q(0) + r (q(1) − q(0)) + q(∞) r (r − 1)`.  The opening message `M[a][b]` is the bivariate `q(X1, X2)` (X1 = the top variable,
τ1 = `tau[n_k + n_c − 1]`; X2 = the next, τ2 = `tau[n_k + n_c − 2]`) in the mixed representation: `b` indexes the X2-representation
(`q(X1, 0)`, `q(X1, 1)`, X2²-coefficient), `a` the X1-representation of each of those three X1-quadratics; so `M[a][b]` for
`a, b ∈ {0, 1}` is `q(a, b)`, and `q(r1, r2) = eval_X2([eval_X1(M[:, b], r1) for b], r2)` with `eval` the univariate rule above.

**Claims out** (`verify` returns them; the PCS must check them against the commitment for the proof to hold):
`claims[0] = w̃(r_i ‖ r_c) = values[0]` and `claims[1 + x] = w̃(bits(c_x) ‖ ρ) = values[1 + x]` for each linked row `x`; the point is
`(n_i + n_c, 6)` in PCS variable order (row bits first; `bits(c_x)` is the committed row index of `sys.chain["c"][x]` as `n_i` 0/1
ext coordinates).  Four claims for fp8-ada; the PCS batches them by its `α` (ligerito-proto).

**Verifier's checks** (what `verify` does; the Rust verifier repeats it): (1) zero-check: opening round
`Σ_{a,b∈{0,1}} eq(τ1, a) eq(τ2, b) M[a][b] = 0`, then `E = eq(τ1, r1) eq(τ2, r2)`, `claim = E · q(r1, r2)`; rounds `t = 2 ..`:
`E_t · ((1 − τ_t) q_t(0) + τ_t q_t(1)) = claim_t`, `E_{t+1} = E_t · eq(τ_t, r_t)`, `claim_{t+1} = E_{t+1} · q_t(r_t)`, where
`τ_t = tau[n_k + n_c − 1 − t]`; final `E · (abc[0]·abc[1] − abc[2]) = claim`. (2) rows: `claim = abc[0] + γ abc[1] + γ² abc[2]`, rounds `q(0) + q(1) = claim`,
`claim ← q(r)`; final `coef̃(r_i) · z̃(r_i, r_c) = claim` with `coef = eq(r_k, ·)ᵀ (A + γB + γ²C)` (a sparse `nnz`-ext-op computation
from the constraint matrices) and `z̃(r_i, r_c) = values[0] + Σ_v eq(r_i, idx_v)·virt_v(r_c)` over the public virtual rows (MLE of each
public `(C,)` vector at `r_c`: const → 1, masks → closed form or a `C`-sum, `pub:*`/`y16` → a `C`-sum each) and the `next_vals`.
(3) shift: `claim = Σ_x g3^x next_vals[x]`, rounds as (2); final `succ̃(ρ, r_c) · Σ_x g3^x values[1 + x] = claim`, `succ̃(a, b) =
Π_{s-bits} eq(a_s, b_s) · MLE of the cyclic successor on the n_j column bits` (`sumcheck.succ_mle`, O(n_j²); `succ_mle_dense` is
the O(l) reference).  `r_*` vectors are indexed by VARIABLE (`r[t]` ↔ bit `t`); the round order binds the top variable first, so
`r_var = reversed(rounds' r)`.

**Constraint matrices for the verifier.** `constraints(sys, lay)` is deterministic from the System: `k` runs over `sys.quadratic`
(in order), then the non-`pin:` `sys.linear` (in order), then the chain rows (`link:x` for each linked row, `start:x`, `end`);
coefficients are `_map_expr` of the affine `Expr`s (pins → their `pub:` row, the constant → the `const` row).  ligerito-verify-rs
needs the same COO triples: they can be emitted once per relation as a fixture (`cons.coo`, `cons.names`, `lay.virt`,
`lay.row_of_sys`, `lay.c_rows`) — ~19k `(k, row, coef)` triples for fp8-ada.

## 4. Reconciliation with ligerito-design / ligerito-proto (18:20Z)

* **Shift design.** Design's note (17:55Z) has no separate shift mechanism — its byte model counts "zero-check 17 rounds of c = 2
  variables + (i, i') 6 rounds + 9 claims".  Mine: the shifted rows are *virtual* rows of `z` (prover-supplied, `W(c_x, ·)` rolled by one
  column, cyclic per sub-batch) so the link constraint is an ordinary row of the zero-check, and one extra degree-2 sumcheck over the
  `n_c` column variables (the "shifted-polynomial identity": `succ̃(r_c, ·)` is the rolled eq table) ties each shifted row to the
  committed one at a fresh point.  Cost measured: 0.115 s (torch; a kernel would make it ~10 ms) + 3 extra claims + 18 × 72 B.  The
  "sparse-matrix" variant is the same prover and the same messages; only the verifier's `succ̃` evaluation differs (`O(l)` vs
  `O(log² l)`) — both are in the code (`succ_mle_dense` / `succ_mle`), the closed form is what `verify` uses.  Design counted 9 claims
  vs my 4: fine either way for the PCS.
* **Bytes / coins.** Design's relation-message estimate 13.4 KiB assumed `c = 2` variables per coin throughout (16 ext per
  zero-check message).  Measured: the two-variable round pays for itself only where the tables are large (it halves the ext volume of
  the whole zero-check when used as the OPENING round: 56 → 37 GB, −90 ms), so I bind two variables there (9 ext elements: the
  bivariate is degree ≤ 2 per variable, so 3 × 3 not 4 × 4) and one variable after: 4645 B, 61 coins.  Going to `c = 2` everywhere
  would cut coins to ~40 at +5 KB and no prover gain; a three-variable opening (27 ext) is the next prover lever (§2).
* **Layout.** Design's `radix3` tall dimension (`3 × 2^16` columns for fp8) vs my `2^18` padded columns: my hypercube needs a power of
  two, so `S = 16` with 13 real sub-batches (`+23 %` cells, matches design's `pow2` line at 2^30).  Design's `rows_pad = 4096` with ZK
  mask rows: compatible — the mask rows must live in rows `[m + 200, 4096)` (296 free rows for fp8-ada) and be part of the prover's
  `z` (they are touched by no constraint; the row sumcheck's `z̃(r_i, r_c)` identity then holds with the masks inside `w̃`).
* **Field / coins / claim order.** Adopted proto's: `F_p[X]/(X^6 − 31)` (`v2/fc.py` is that field; Ligero's `protocol.py` "D
  coordinates" is not and is not used), `bytes` labels, absorb-then-challenge, `x = row + R·col`.

## For ligerito-relation

* You call, per batch: `lay = layout_for(sys, l, n_vus, steps)`, `cons = constraints(sys, lay, device)` (once per relation — cache it),
  `subs = [SubBatch(W_s, pub_s, ypub_s, n_vus_s)] * S` (pad sub-batches: `W` of pad units, `ypub = 0`, `n_vus = 0`;
  `sumcheck.ligero_subbatches` shows the exact Ligero calls, `_marshal_pad` the pad one), `z = build_z(sys, lay, subs, device)`,
  `proof = prove(lay, cons, z, coins, engine="cuda")`, then hand `proof.claims` (4 `EvalClaim`s) to the PCS and `proof.to_bytes()` to the
  wire.  The committed polynomial is `f[i + R·c] = z[i, c]` for `i < lay.m` and 0 for `i ≥ lay.m` (i.e. `z` with the virtual rows
  zeroed, transposed to column-major, flattened) — build it from `z` before `prove` (which does not need it) or from `W` directly.
* `z` is `(4096, 2^18)` int32 = 4.3 GB; `prove` peaks at 37 GB including `z` (H100 only; see §2 for the 4090).  Everything is on the
  caller's device; `prove` allocates and frees its tables.  0.36 s per 4096-VU batch on the H100.
* Timing knobs in `proof.timings`: `tables`, `sumcheck1` (+ `sumcheck1_rounds` list), `sumcheck2`, `sumcheck3`, `total`.
* Pins: not committed.  Your witness `W` still has them (Ligero's `build_witness` produces `sys.m` rows); `build_z` drops them via
  `lay.row_of_sys`.  The pub vectors must include every name in `sys.pins` and every `Linear.pub` (`rel.public_vectors` does).
* Verifier side: `public_rows(sys, lay, [s.public() for s in subs], device)` then `verify(...)`; `coins` must be a fresh object in the
  same state as the prover's after the commitment absorb.

## For ligerito-verify-rs

* Parse §3's wire format; run §3's "verifier's checks" with `F_p[X]/(X^6 − 31)` arithmetic (`p = 2^31 − 2^27 + 1`); draw every coin in
  §3's call order from the shared transcript (labels are the literal ASCII strings; the absorbed bytes are exactly the wire bytes of
  the message named).  Reject non-canonical coordinates.
* Verifier work: `nnz ≈ 19.5k` ext × base products for `coef`, the `eq` tables of `r_k` (4096) and `r_i` (4096), the public-row MLEs
  at `r_c` (192 vectors × 2^18 base × ext — 5·10^7 base×ext products ≈ 10 ms; or ask the relation lane for `pub` MLE evaluation in
  closed form where the vectors are structured), `succ_mle` (closed form below), 30 + 12 + 18 round checks.
* `succ̃(a, b)` on `n_c = n_s + n_j` variables (`a` = the shift sumcheck's ρ, `b` = `r_c`): `Π_{t ≥ n_j} eq(a_t, b_t)` (same sub-batch) ×
  `Σ_{u=0}^{n_j−1} [Π_{t<u} a_t (1 − b_t)] · (1 − a_u) b_u · Π_{t>u} eq(a_t, b_t)` + `Π_{t<n_j} a_t (1 − b_t)` (the wrap `l−1 → 0`); i.e.
  `b = a + 1 mod l`: the low `u` bits of `a` are 1 and of `b` are 0, bit `u` flips 0→1, higher bits equal.  `sumcheck.succ_mle` is
  the reference; `succ_mle_dense` (O(l)) checks it.
* **Fixture (18:30Z):** `~/.research/notes/lanes/ligerito-sumcheck/evidence/fixture_fp8ada_l64_S2.json.gz` (688 KB unpacked;
  `python -m backends.direct.ligerito.sumcheck --fixture PATH` regenerates it on a torch machine): fp8-ada, `l = 64`, `S = 2`, 2 VUs,
  `N = 2^19`.  Keys: `layout` (`m, n_i, n_j, n_s, n_k, K, R, C, virt {name -> row}, c_rows, row_of_sys`), `constraints` (`K_pad`,
  `names[k]`, and `a`/`b`/`c` = three lists `[k[], row[], coef[]]` of the COO triples, 19458 in all), `public_rows` (`name -> [C]`
  ints, the verifier's virtual rows), `proof_hex` (3061 B = the LGSC0002 wire form; `n_c = 7` here), `claims` (4 × `{name, point
  [[6] × 19], value [6]}`, point in PCS order row-bits-first), and `transcript`: the 80 absorb/challenge events in protocol order with
  the absorbed bytes (hex) and the drawn values — replay them with a scripted coins object and your verifier must accept and produce
  exactly these claims.  The coins are `LocalCoins(b"fixture")`: `challenge(label, n)` = SHAKE-256(`b"fixture|" + label + b"|" +
  u32le(round)`), `8·6·n` bytes, each u64le mod p, `round` counting challenges from 0 (absorbs ignored) — implement it or just replay.

## 5. What integration still needs

1. **ligerito-relation**: the PCS input `f[i + R·c] = z[i, c]` for `i < m` (0 elsewhere) built from `z` (or from `W` directly); a
   single `coins` object shared with the PCS in the order commitment → this module's 61 draws → PCS opening rounds; ZK mask rows, if
   the PCS wants them in the polynomial, go in rows `[m + 200, 4096)` and into the prover's `z` (§4).
2. **ligerito-verify-rs**: implement §3's checks from the fixture; the public-row MLEs at `r_c` are the only O(C) verifier work — the
   relation lane should say which `pub:*` vectors have closed forms (the fp8 exponent/mantissa decodes are functions of the public
   words, so their MLEs at `r_c` are sums over the 4096 × 48 public words, not over 2^18 columns).
3. **The 4090 cell**: half-batches (2048 VUs, 18.6 GB) or a striped zero-check; measure on a 4090 (I had no 4090; the H100 numbers
   and the linear-in-N scaling are what I can give).
4. **Kernel floor** (optional): trivariate opening (−60 ms), fused fold + next message (−10 %), `coef` on the device (−20 ms) → ≈ 0.2 s.
5. **Soundness accounting**: `(K + 3 + 30 · 3 + 12 · 2 + 18 · 2 + 4) / p^6 < 2^-170` for the batching and sumcheck terms; the pin
   rows are public, so nothing is committed that the verifier does not need — ligerito-design's soundness table can drop the
   `pin:` constraints from `Lin`.

## IR requests
none.  (`compile.py` untouched; the layout reads `System.rows/linear/quadratic/pins/chain` as they are.  One wish, not a request:
a `System.pub_names` list — today the layout collects the public vector names from `sys.pins` and `Linear.pub`.)

## FINAL (18:45Z)

* Branch `lane/ligerito-sumcheck`, head **5b33e23** (7 commits over `main` e0cf2cd), `git status --short` empty; files touched:
  `backends/direct/ligerito/layout.py`, `sumcheck.py`, `sumcheck_test.py`, plus the package marker `backends/direct/ligerito/__init__.py`
  (a 4-line docstring; the directory did not exist on `main` — ligerito-proto's branch creates the same file; take either at merge).
  `compile.py` untouched.
* Chain shift: shifted virtual rows in `z` (`Wnext_x = W(c_x, ·)` rolled by one column, cyclic per sub-batch) + one degree-2 sumcheck over
  the 18 column variables tying them to the committed rows at a fresh point; cost 10 ms of 291, 3 extra PCS claims, 18 × 72 B + 3 × 24 B
  of messages.  The sparse-matrix form is the same prover; only the verifier's `succ̃` evaluation differs (closed form used).
* fp8-ada 4096 VUs on the H100, steady state: **0.291 s** per batch (tables 0.023 · zero-check 0.220 [65, 49, 25, 13, 6.5, 3.5, 2, 1.2,
  0.9, 0.6, 0.4 ms, then 18 × 0.3 ms] · rows 0.038 · shift 0.010) vs `t.arithmetic` 0.209 s = **1.4×**; 0.365 s cold; peak 37.1 GB.
  bf16-hopper 4096 VUs: 0.482 s, 73.6 GB.  fp8-ada 2048 VUs: 0.190 s, 18.6 GB.
* Messages **4645 B** (fp8-ada; 4789 B bf16 at `S = 32`), 61 coins; format LGSC0002 in §3; fixture in `evidence/`.
* Negatives at real N: violated quadratic row / chain link / lookup → honest prover fails round 0, round-fixing prover fails the final
  claim; plus shift-inconsistent prover, wrong coins, opening-round-only cheat (toy).  CUDA path byte-identical to the torch reference.
* Pod `k8ixstiy66e1lx` (H100 80GB, $3.49/h) 17:42Z–18:39Z, ≈ $3.3, terminated.
* Integration still needs §5: the PCS input from `z`, shared coins order, the 4090 half-batch decision, the Rust verifier from §3 + fixture.
