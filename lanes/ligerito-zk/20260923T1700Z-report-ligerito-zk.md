---
lane: ligerito-zk
kind: report
created: 2026-09-23T17:00Z
status: final
---

FINAL f8eee3e (19:05Z) — see `## FINAL` at the end. Pod `vy-ligerito-zk` = blstbyj7sh2xyk (RTX 4090 reference part, $0.74/h) created ≈18:20Z, terminated 18:58Z: ≈ 0.65 h ≈ $0.50 of the $4. 17 numpy tests (laptop + pod) and 5 device tests (pod) pass at f8eee3e; `git status --short` empty.

CHECKPOINT 318ec9b (19:00Z) — pod measurements done (§7); read ligerito-sumcheck's Interface (18:20Z; `f[i + R c] = z[i, c]`, row bits LOW, bivariate opening round, claims `w~(bits(c_x) || rho)`), ligerito-proto's FINAL (0.525 s PCS prover at 2^30) and red-team-ligerito's F1/F3/F6/F7 (18:50Z handoffs) → §1.0b below: the column-block geometry of §1.0 is INFEASIBLE in the real layout (F6 confirmed independently), replaced by MASK ROWS + a bit-interleaved PCS index map (`RowMaskLayout`, `z_to_f`, `permute_point`, `fill_mask_rows`); the eq-weighted Libra mask with a cross block for the bivariate opening round (`EqSumcheckMask`, closes F3, keeps Gruen's 3-value wire form); `queries_for` union default (F7); two NEW leaks found in the sumcheck lane's protocol as posted (shift-claim boolean row points; `abc` — the latter already covered by the product rows). `## For ligerito-relation` posted.

CHECKPOINT deea857 (19:05Z-labelled; the clock labels of the two earlier checkpoints were estimates and are ~1 h early — `date -u` is used from 19:00Z on) — `zk.py` (masks, padding hooks, Libra `SumcheckMask`, committed coins, fingerprint text), `zk_stub.py` (toy Ligerito + zero-check, interactive, simulator), `zk_test.py` (15 pass, 35 s, numpy only) committed; §1.0 corrections below (8-column mask blocks at both ends instead of one column + A-cells; Libra masks for every sumcheck); 17:30Z HARD RULE acknowledged: no torch on the laptop, GPU work on the pod only (`zk.py` is numpy, torch imported lazily); no pod yet — next: refactor `zk.py` to the §1.0 shape (both-end mask blocks, several `SumcheckMask`s), then the pod cost measurement.
CHECKPOINT none (17:55Z) — briefs, PROTOCOL.md 8b/8c, protocol.py masking, redteam_zk.py, both red-team-zk notes, the Ligerito paper §3–§6, Libra §4.1 (ePrint 2019/317), CFS17 (ePrint 2017/305) read; worktree `~/projects/verity-main-wt/ligerito-zk` on `lane/ligerito-zk` from e0cf2cd; design below (§1–§5); `zk.py` next; no pod yet.

# ligerito-zk — malicious-verifier ZK for the zero-check sumcheck + the Ligerito openings

Scope (wave-B brief §2.3): design first, then `backends/direct/ligerito/zk.py` (hooks for `pcs.py` and `sumcheck.py`), a
measured cost at real N on the pod, a simulator test that separates a mask-free proof, the `omitted`/`zk_statement` text.

## 0. What leaks in plain Ligerito (paper §3–§6 applied to our relation) — the list the masking has to cover

Prover messages, in order, with what each is as a function of the witness polynomial `f` (N = 2^n base cells):

| # | message | leak (as a functional of `f`) | count |
|---|---|---|---|
| L1 | zero-check round messages `h_j(0..3)` | degree-3 (quadratic in `f`) partial sums | `3n + 1` independent values (4 per round minus the `h_j(0)+h_j(1)=h_{j-1}(r_{j-1})` redundancy; Libra §4.1 counts `nd + 1`) |
| L2 | evaluation claims `v_i = f(z_i)` at the sumcheck point(s) (+ shifted points for the chain) | linear, `eq(z_i, .)` | `E` (2–4) |
| L3 | PCS round-`i` partial-sumcheck messages `g_j(0..2)` (over the `k'_i` column variables) | linear in `u^{(i)} = M~_i^T rowpart` (one value per column) | `2k'_i + 1` per committed round |
| L4 | "expected symbols" `<gen_s, y_{i}>`, `s in S_i` (paper §6.2 step 4.1; sent so the verifier can check the opened rows) | linear in `y_i = M~_i r-bar_i` = `f` folded | `|S_i|` per committed round `i >= 1` (the last round's are computed by V from L6) |
| L5 | opened rows `U_i[s, :]`, `s in S_i` | one linear functional (RS evaluation at `eta_s`) of every column of `M~_i` | `|S_i| x 2^{k'_i}` per round |
| L6 | final vector `y_ell` (in the clear) | `f` with every column variable folded: `2^{k_{ell-1}}` linear functionals | `2^{k_{ell-1}}` (1024 at N = 2^29) |

L4 is the one that is easy to miss: it is what the Ligero-8b "proximity message `w = rU + s_prox`" becomes in the recursion,
and its mask has to be a *committed* object that folds along with the witness, not a per-column padding (padding hides L5
but its `r-bar`-combination is exactly what L4 reveals). Constant / structured rows of our witness (35 % of opened values
were `0` before 8b) make every one of L1–L6 distinguishable from a proof of the trivial witness.

## 1. Design (decided; costs in §4)

### 1.0 CORRECTIONS 19:05Z (found by the toy end-to-end run + simulator; supersede §1.1's M-col / A-cells wording)

Two things the first draft got wrong, and the resulting design (implemented in `zk.py` at CHECKPOINT deea857+):

**(a) Base masks vs extension functionals.** Every leaked value (a fold entry `y_i[row]`, an eval claim `f^(z)`, a round-1
contraction `u[c]`, a sumcheck message) is an F_{p^6} element `sum_x w_x f^[x]` with extension weights `w_x`, while mask
cells are BASE-field. One uniform base cell blinds only the F_p-line `F_p . w_x` (1 of 6 coordinates): the "one mask
column" of the draft would have leaked 5/6 of every `y_1` entry. Fix: every functional must reach **>= 6 uniform base
cells whose weights span F_{p^6} over F_p**. Eight cells forming a 3-bit sub-cube have weights `{prod_j pair_j(b_j)}` (tensor
factors of 3 random extension coordinates), which span with probability `1 - O(1/p)` (the exact F_p-rank test in
`zk_test.py::test_exact_rank_of_leaked_functionals_on_mask_cells` passes; the failure event is the simulator's rank term).
So: mask ROWS come in blocks of 8 round-1 columns.

**(b) Which functionals the masks actually reach — the layout decides.** (i) An eval claim `f^(z)` whose point has BOOLEAN
coordinates on the bits that separate the mask region from the constrained region has weight 0 on every mask cell — it is a
bare functional of the witness. In ligerito-sumcheck's design the zero-check (sumcheck 1, over `(k, c)`) ends in sub-cube
claims `Az(r), Bz(r), Cz(r)` and their sumcheck 2 (over the 12 ROW bits, all 4096 rows incl. the zero rows) turns them into
ONE claim `w~(r_i, r_c)` at a fully-extension point — that claim reaches the mask rows (they are rows). Good: no change
needed for them; the requirement is simply "the PCS eval claims are at points with no boolean coordinate on the mask
rows' bits" (the toy models sumcheck 2 explicitly). (ii) A sumcheck message is `sum over half the cube` of `public(x) .
witness-table(x)`; a mask cell enters only if the PUBLIC factor is non-zero at it. For the ROW sumcheck the public factor
is `alpha(i) = eq(r_k, .)^T A` which is exactly 0 on the zero rows — mask rows do NOT enter; same for the shift sumcheck.
So **every sumcheck over witness tables gets its own Libra mask** (`SumcheckMask`, one G-block each, all coefficients in
the last mask column): zero-check `(n_k + n_c = 30 vars, d = 3)`, rows `(12, 2)`, shift `(18, 2)` = `91 + 25 + 37 = 153`
extension coefficients = 918 base cells; three `rho` coins; three block claims batched into round 1. (iii) The round-1 PCS
partial sumcheck over the `k'_1` column bits: its public factor (the tensor `colpart`) is non-zero everywhere, so mask
COLUMNS do enter — but the round-`j` message `h(0)` sums only the columns whose bit `j` is 0: both halves of every bit
split must contain a mask column, at every fold. Mask columns at BOTH ENDS of the column range do it: `{0}` and `{C_1-8..
C_1-1}` (fold: `u'[c] = (1-r) u[c] + r u[c + C/2]` keeps a mask at both ends). `u[c_mask]` is a full-column functional
(`2^{k_1}` uniform cells) hence uniform, so the 2 free extension values per round are uniform. The A-cells of the draft
(8 free cells inside EVERY round-1 column) are dropped: fp8-ada's layout has no free cell inside its committed rows.

**Resulting layout ask (for ligerito-sumcheck, §3):** with `k'_1 = 7` (C_1 = 128 round-1 columns = 16 layout rows each):
zero rows at the TOP `[4096 - 128, 4096)` (the top 8 columns) AND at the BOTTOM `[0, 16)` (column 0) — i.e. committed rows
live in `[16, 3793)`; 3777 rows fit. Both are inside the 319 zero rows the layout already has → **0 extra cells, 0 extra
rows**; a layout with no spare rows would pay `9 / C_1 = 7 %` of N. `check_layout` enforces it.

**What the toy measured (n = 2^15, 3 committed rounds, |S| = 16, t_pad = 24; `zk_test.py`, 15 tests, 35 s):** honest
proofs accept with and without masks; tampering `y_ell`, `ybar`, `g(r)`, a message, or the witness is rejected; the
simulator (dummy run → rewind → fake tableau with the G-block re-solved so `sum g* = G*` and `g*(r) = v_g*`, mask cells
solved so `f^*(z) = v*`, then the honest prover) yields ACCEPTING transcripts against honest, equivocating (aborts at the
same slot with the same public prefix as the real prover), zero-coin and public-check-aborting verifiers; two-sample
chi-square (64 bins, 6 proofs each) real-vs-simulated is `p in [0.11, 0.94]` on all 10 components (zero-check messages,
evals, PCS messages, opened rows x3, `ybar` x3, final vector) and structured-vs-trivial-witness (masked) `p in [0.30,
0.99]`; the SAME comparison mask-free is `p < 1e-17` on every component (final vector `chi2 = 17830`, and the trivial
witness's final vector is identically 0: a perfect distinguisher). Padding rate at real N: `(2^15 + 256)/2^17 = 0.252` →
`|S|` 192 → 193 (not 202 as §4 said).

### 1.0b CORRECTIONS 19:00Z — the REAL layout (ligerito-sumcheck 18:20Z) kills the column blocks; mask ROWS + an interleaved index map replace them

ligerito-sumcheck commits `f[i + R c] = z[i, c]` (`R = 2^12` rows, `C = 2^18` columns; row bits LOW), every column `c` is a
constrained unit column (the 3 pad sub-batches hold VALID pad witnesses — random cells there break `Az∘Bz = Cz`), and the only
unconstrained cells are rows `[m + 200, 4096)` (296–319 rows) in EVERY column. So a round-1 PCS column (the top `k'_1` bits of `x`
= a slice of `2^{n_c - k'_1}` relation columns, all rows) can never be uniform: §1.0's "8-column blocks at both ends" is infeasible
(red team F6 says the same). The primitive that exists is a **mask row**: a free relation row, `2^18` uniform base cells. What
mask rows reach, with the weights being tensor products of challenges (generic on every cell):

* every round-`i` column contraction `u_i[c]` and BOTH halves of every column-sumcheck split at every round (a relation row
  meets every PCS column of every round) — so the PCS recursion's messages are masked without both-end blocks;
* the eval claims at fully-extension points (`w~(r_i, r_c)`), the block claims;
* **the final vector `y_L[rho]` — indexed by the LOW `k_L` bits of `x`.** With row bits low, `rho = i mod 2^{k_L}` (`k_L ≤ 12`):
  a mask row masks only the entries `rho ≡ i` — covering all `2^{k_L} = 1024..8192` entries needs `2^{k_L}` mask rows. Impossible
  in 319 free rows. **Fix (pure glue, no module changes): interleave `a = k_L - 3` COLUMN bits below the row bits,
  `x = (c mod 2^a) + 2^a i + 2^{a + 12} (c >> a)`** (`zk.f_index` / `zk.z_to_f`: one transpose of the `(2^{n_c-a}, R, 2^a)` view,
  9.5 ms on the 4090 at 2^30). Then `rho = (c mod 2^a, i mod 8)` and **8 mask rows with distinct residues mod 8** give every final
  entry `2^{18-a} = 2048` uniform cells. Round-1 PCS columns are unchanged (still the top `k'_1` bits of `c`); the sumcheck lane's
  row-bits-first claim points are permuted by `zk.permute_point` (tested: the MLE of `f` at the permuted point equals the MLE of
  `z` at the original point).
* the zero-check's final `Az(r), Bz(r), Cz(r)` (`abc` in the sumcheck lane's wire form) are bare witness functionals (A, B, C are
  0 on free rows): the §1.0 product-row constraint `m1 · m2 = m3` on three COMMITTED rows handles it — the relation adds one
  quadratic constraint row, the prover fills `m1, m2` uniformly and `m3 := m1 · m2` (`fill_mask_rows`).
* **NEW LEAK (sumcheck lane's protocol as posted): the shift sumcheck's claims `values[1 + x] = w~(bits(c_x) || rho)` have BOOLEAN
  row coordinates** — each is `sum_c eq(rho, c) z[c_x, c]`, a bare functional of the chain row `c_x` (3 extension elements = 18
  F_p functionals of the witness per proof), sent in the clear. No mask row reaches them. Fix (ligerito-sumcheck, +12 tiny rounds):
  reduce the three claims by one more rows-type sumcheck over the 12 row variables at column point `rho`
  (`sum_x g^x eq(bits(c_x), i) · z~(i, rho)`; the table `z~(·, rho)` is a 4096-vector the shift final already computes), ending in ONE
  claim `w~(r_i', rho)` at an extension row point — masked by the mask rows; its messages get their own `EqSumcheckMask`
  (public factor `eq(bits(c_x), i)` vanishes on mask rows). +12 × 72 B, +12 coins.
* **Red team F3 (Libra vs the bivariate opening round) — fixed in `zk.EqSumcheckMask`:** the mask is multiplied by the SAME
  public `eq(tau, x)` factor as the witness summand, so the prover's round message stays Gruen's `(q(0), q(1), q(inf))` of
  per-variable degree 2 (no degree-3 wire form), the verifier's checks are unchanged except the initial claim becomes `rho · G`
  with `G = sum_x eq(tau, x) g(x) = a_0 + sum_i tau_i g_i(1) + tau_0 tau_1 sum c_ab` (sent), and `g` gains a `2 × 2` cross block
  `sum_{a,b} c_ab x_0^a x_1^b` for the opening pair, so the 9 coefficients of the `3 × 3` opening message are spanned
  (`1 + 2 + 2 + 4 = 9`; the separable mask leaves the `X1^a X2^b` coefficients in the clear — `zk_test.py::test_eq_sumcheck_mask_bivariate_opening_and_rounds`
  checks every verifier identity against brute force and the separable/non-separable distinction). Zero-check mask: `1 + 2·30 + 4 = 65`
  coefficients; rows 25; shift 37 → 127 F_p^6 = 762 base cells in the Libra row.

**Resulting cost (fp8-ada, R = 4096, C = 2^18, N = 2^30): 8 uniform rows (free region, 0 extra cells) + 3 product rows + 1 Libra row
(4 of the ~296 spare committed rows) = 12 rows = 3.1 M cells = 0.29 % of N**; measured fill 0.72 ms on the 4090 (§7).

Notation follows `ligerito-proto`'s note: round `i` commits `M~_i` (`2^{k_i}` rows x `2^{k'_i}` columns, column-major,
`x = row + 2^{k_i} col`, the column bits are the HIGH variables), RS in coefficient basis along the tall axis, codeword
length `n_i`, opened row set `S_i`; at N = 2^29: `k' = (7, 4, 4, 4)`, `k = (22, 18, 14, 10)`, final vector `2^10`.
Field: BabyBear, challenges in `F_{p^6} = F_p[x]/(x^6 - 31)` (proto's `ext.py`; I reuse it, I do not reinvent it).

### 1.1 Mask cells inside the committed polynomial (Ligero-style mask rows, adapted to the recursion) — covers L2, L3, L4, L6

The prover's polynomial is `f^ = f + masks`, where the masks occupy cells that NO constraint is located at or references
(a layout requirement, §3). Three groups, all sampled by the device ChaCha20 sampler (`mask_sampler.py`, rejection to
BabyBear, exactly uniform):

* **M-col — the mask column**: the top round-1 column, cells `[N - 2^{k_1}, N)` (all round-1 column bits = 1), uniform.
  Its whole point: `y_1 = M~_1 r-bar_1 = (payload fold) + r-bar_1[C_1 - 1] . m` with `r-bar_1[C_1-1] = prod_j r_j != 0`
  w.h.p., so `y_1` is a **uniform** vector of length `2^{k_1}`, independent of the witness; every later round works on a
  fold of `y_1`, which stays uniform (`y_i = M~_i r-bar_i`, a fold of a uniform vector is uniform). Hence L4 (all rounds),
  L3 for rounds `i >= 2`, L6 (the final vector) and L2 (`v_i = f^(z_i)` contains `eq_high(z_i, top) <eq_low(z_i), m>`)
  are all functionals of a uniform vector of dimension `2^{k_1} = 4M` — the total number of them is `~2^11`; the
  rank condition is generic in the challenges (exact rank checked in the toy simulator test, §5).
  At N = 2^29 that is `1/C_1 = 1/128 = 0.78 %` of the cells; fp8-ada's flat layout has 9 % padding rows (3724 -> 4096)
  and 25 % padding columns (196 608 -> 2^18) so the top column is padding anyway (cost 0 if the layout packs from 0).
* **A-cells — one mask cell per round-1 column**: `x = c . 2^{k_1} + q` for `c < C_1 - 1`, `q` a padding row offset
  (e.g. row 4095 of the 4096-row Ligero column if rows are the low 12 bits). Round 1's partial sumcheck is over
  `u^{(1)}[c] = <rowpart, M~_1[:, c]>`: the mask column gives ONE degree of freedom (`u[C_1-1]`), the A-cells give one
  uniform summand `rowpart[q] m_c` in every other column, so `u^{(1)}` is uniform in `F^{C_1}` and its `2k'_1 + 1 = 15`
  leaked functionals (L3, round 1) are masked. Cost: 127 cells.
* **G-block — the Libra mask polynomial for the zero-check** (§1.3): `3n + 1` extension coefficients = `6(3n+1) ~ 550`
  base cells, stored inside the mask column (they are uniform too; they only get one extra claim, §1.3).

Why not a Libra-style mask for L3–L6 instead: L6 alone is `2^{k_{ell-1}}` values and every message of every PCS round
is a functional of the same folded vector, so a mask that is a small polynomial in the sumcheck variables cannot reach
them; one uniform column that folds with the witness is the cheapest object that does (0.78 % of cells, or 0).

### 1.2 Per-column RS padding + the in-the-clear padding combination — covers L5

Every column of every committed `M~_i` is encoded from the message `(M~_i[:, c] || mu_c)`, `mu_c in F^{t_pad}` uniform,
message length `2^{k_i} + t_pad` (coefficient basis: `x^{2^{k_i}} mu_c(x)`; the codeword length `n_i` is unchanged when
`n_i >= 4 . 2^{k_i}` leaves room, which it does). Values of `mu_c` at any `t <= t_pad` distinct points `eta_s` are uniform
(Vandermonde), so `U_i[s, c] = payload_c(eta_s) + mu_c(eta_s)` is uniform for `|S_i| <= t_pad`: **`t_pad = 256`** (Ligero
8b's; `|S| = 192`). The row check needs the padding's `r-bar`-combination: the prover sends **`ybar_i = mu^T r-bar_i`**
(`t_pad` extension elements, 6 KB) in the clear together with the next commitment, and the verifier checks, for `s in S_i`,

    < U_i[s, :], r-bar_i >  =  < gen_s, y_i >  +  < gen'_s, ybar_i >,     gen_s = (eta_s^x)_{x < 2^{k_i}},  gen'_s = (eta_s^{2^{k_i} + j})_{j < t_pad}

i.e. the claimed combination is the concatenated message `(y_i || ybar_i)` — `y_i` committed as `M~_{i+1}` (a tensor claim
as before, the recursion is untouched), `ybar_i` public. Soundness: `ybar_i` is fixed BEFORE `S_i` is drawn (it travels
with `root_{i+1}`), so the check is the paper's matrix-vector consistency check for the message `(y_i || ybar_i)` with
message length `2^{k_i} + t_pad` — the RS rate of round `i` becomes `(2^{k_i} + 256) / n_i` and `|S_i|` must be sized for
it (§4: nothing at rounds 1–2, +2 at round 3, +22 at round 4 unless round 4's codeword is doubled, which is cheaper).
ZK: the joint distribution of `((mu_c(eta_s))_{s,c}, mu^T r-bar)` is uniform on the subspace `{sum_c r-bar[c] a_{s,c} =
<gen'_s, b>}` (kernel dimension `(C-1)(t_pad - t)` exactly, image = the consistency subspace), so opened rows + `ybar` are
uniform given the expected symbols `<gen_s, y_i>` — which are masked by §1.1. Padding also hides the mask column's own
openings and the G-block. A verifier that pre-selects `S_i` (statement-adaptive, red-team-zk A5) is covered for any
`|S_i| <= t_pad`.

### 1.3 Zero-check masking — Libra §4.1 / CFS17 (covers L1)

The zero-check is `sum_x eq(tau, x) C(x) = 0`, degree `d = 3` per variable (`eq` x quadratic constraint). Libra
(Xie–Zhang–Zhang–Papamanthou–Song, CRYPTO'19, ePrint 2019/317 §4.1, Construction 1 + Theorem 3), the cheap instance of
the CFS17 masked sumcheck (Chiesa–Forbes–Spooner, ePrint 2017/305): the prover samples

    g(x) = a_0 + sum_{i<n} g_i(x_i),   g_i(X) = a_{i,1} X + a_{i,2} X^2 + a_{i,3} X^3,   a_. in F_{p^6} uniform  (3n + 1 coefficients),

stores the coefficients in the G-block of `f^` (committed with the witness), sends `G = sum_x g(x) = 2^n a_0 + 2^{n-1}
sum_{i,e} a_{i,e}` after the commitment, receives the coin `rho_zk`, and the sumcheck runs on
`sum_x [eq(tau, x) C(x) + rho_zk g(x)] = rho_zk G`. Round `j` adds `rho_zk . 2^{n-1-j} [a_0 + sum_{i<j} g_i(r_i) + g_j(X)
+ (1/2) sum_{i>j} g_i(1)]` at `X in {0,1,2,3}` (O(n) per round). The final check is `C(v_1, ..., v_E) + rho_zk v_g =
h_n(r_n)` with `v_g = g(r) = a_0 + sum_i g_i(r_i)` sent by the prover and **verified as an inner-product claim on `f^`**:
`< W_g, f^ > = v_g`, `W_g` supported on the G-block with weight `x^d r_i^e` at the cell holding coordinate `d` of
`a_{i,e}` (`x^d` = the extension basis element). Libra Thm 3: the `3n + 1` independent linear constraints the verifier
learns on the summand's coefficients are matched by `3n + 1` uniform mask coefficients, so the message distribution is
identical for every `f` (the sum `rho G` and the final `g(r)` are the `+1` and the redundancy). Soundness: the random
combination adds `1/|F_{p^6}| ~ 2^-186`; the mask cells are committed before `rho_zk`, so the prover cannot fit `g`.

`W_g` is a claim with a tensorizable high part (one-hot on the column bits of the mask column, every round) and an
arbitrary sparse low part (`<= 6(3n+1)` non-zeros inside one final chunk): the "block term" of §6 (Interface).

### 1.4 Coins — keeping 8c in a 60-message protocol

Every verifier message `k = 1..K` (`tau` + the `rho_q` batching coins, `rho_zk`, the `n` zero-check challenges, and per
committed round `i`: `S_{i-1}`, the batching `alpha_i`, the `k'_i` partial-sumcheck challenges; then `S_{ell-1}`) is a
**slot** committed at step 0: `c_k = Blake2b(tag || k || r_k || s_k)`, `r_k, s_k` 32 uniform bytes; `K ~ 1 + 1 + n +
sum_i (2 + k'_i) + 1` (about 60 at N = 2^29; `K` is a function of the parameters, known at step 0). The prover's first
message comes after all `K` commitments. Slot `k` is opened right after the prover message it must follow; the prover
checks `c_k`, aborts publicly on mismatch (`CoinOpeningError`, having sent only blinded messages); the challenge is

    chal_k = SHAKE-256( Blake2b("ligerito-zk/coin|v1" || stmt || C || k || r_k) ),   C = Blake2b(c_1 || ... || c_K)

— a function of the verifier's step-0 coins alone (8c, red team F2): no prover message enters any seed, `stmt`/`C`/`k`
are domain separation. Row sets `S_i` are drawn from the same stream with repeats rejected (deterministic, no
prover-controlled restart). Soundness: unchanged interactive statistical bound + the hiding term `K x 2^64 / 2^256`
(`~2^-186`, in the union). Sequential depth `K + 1`; live-2's coin stream / pipelining is orthogonal (their §2.6 item 4).
`transcript.py` (ligerito-proto) owns the `Coins` protocol; `zk.py` provides the slot schedule, the committed-coin
implementation (`CommittedCoins`: honest, deterministic from a seed) and the malicious ones for the tests (§5).

### 1.5 What the verifier never sees, and what it does

Never: any cell of `f` (opened rows are uniform), any un-masked functional of `f` (every message is uniform on its public
consistency set), `f(z_i)` itself (the `v_i` are `f^(z_i)`, uniform through the mask column). Public consistency sets the
messages must lie on (this is what the simulator samples, red-team-zk-2 G1): `h_1(0)+h_1(1) = rho_zk G`, `h_j(0)+h_j(1) =
h_{j-1}(r_{j-1})`, `C(v) + rho_zk v_g = h_n(r_n)`; per PCS round the same for `g_j`; row checks as in §1.2; the final
`< w~_ell, y_ell > = claim`.

## 2. Simulator (interactive, malicious `V*`) and the distance argument

`S` gets the statement and `V*`. GK/HM96 as in PROTOCOL.md 8c, now over `K` slots:

1. Receive `c_1..c_K`. **Dummy run**: `S` plays a prover with no witness: commits to a *genuinely random* `M~_1^0` (uniform
   cells, real Merkle tree; so any opening it is later asked for is honest and consistent with the root — `V*` cannot
   tell the dummy run apart by a Merkle failure), sends `G^0` uniform, then for every slot: receives the opening (or an
   abort, which `S` outputs and stops), and sends the next message drawn from the **honest-observable distribution**:
   sumcheck messages uniform on their consistency affine line, `v_i` uniform, `v_g := (h_n(r_n) - C(v)) / rho_zk`,
   each later round a fresh uniform committed matrix, expected symbols `:= <U[s,:], r-bar> - <gen'_s, ybar>` computed from
   its own openings, `ybar` uniform, final vector uniform. Every check `V*` can run *before its last coin* passes in
   the dummy run exactly when it passes against the real prover (the only checks that fail are the ones that need the
   final vector against earlier claims, which come after the last slot). Output: all `K` openings `(r_k, s_k)`.
2. Rewind `V*` to after step 0. `S` now knows every challenge (`tau, rho, r, alpha, S_i, ...`). It builds a **fake tableau**:
   `f^*` uniform cells everywhere, with the G-block solved so that `sum g* = G*` and `g*(r) = v_g*`, and the mask column /
   A-cells adjusted so that `f^*(z_i) = v_i*` for uniform `v_i*` (`E` linear equations in `2^{k_1}` unknowns); zero-check
   messages sampled uniform on the consistency lines from `rho_zk G*` down to `h_n(r_n) = C(v*) + rho_zk v_g*`; then it
   runs the **real Ligerito prover** (with fresh padding `mu*`) on `f^*` for the claims `{v_i*, v_g*}` under the known
   coins. Commits, replays `V*`: by binding it opens the same coins or aborts (Goldreich–Kahan); abort -> output the abort.
3. Indistinguishability, component by component: L5 + `ybar` — uniform on the consistency subspace in both worlds (§1.2,
   exact); L4, L3 (`i >= 2`), L6, L2 — functionals of the uniform `r-bar_1[C_1-1] m` in both worlds; L3 round 1 —
   functionals of a uniform `u^{(1)}` in both worlds; L1 — Libra Thm 3 (identical linear systems on `3n+1` uniform
   coefficients). The joint view is the image of one uniform tableau under the same linear+hash map in both worlds
   given the claims, and the claims (`v_i`, `v_g`, `G`) are uniform / determined identically.

Distance of the simulation: (i) mask sampling: 0 (rejection) + ChaCha20's PRF advantage on a fresh key; (ii) the
generic-rank events — some tensor weight `r_j`, `1 - r_j` or `r-bar_1[C_1-1]` is 0, or the `E` `eq`-functionals on the
mask column are dependent: `<= (n + E^2 + K) / p^6 ~ 2^-178`; (iii) coin binding (an equivocating `V*` = a Blake2b
collision, `2^-128` at `2^64` work); (iv) **Merkle hiding of unopened leaves — the same ROM-flavoured item as Ligero
(red-team-zk-2 G3)**: leaves are `Blake3(row)`, rows are marginally uniform but jointly correlated; salting the leaves
(`+32 B` per leaf, `+32 |S|` bytes per round) removes it — not done here, listed in `omitted`; (v) GK rewinding: expected
`1/(1-p)` rewinds against a `V*` aborting w.p. `p`, the implementation caps rewinds (same caveat as 8c G2).

**The assumption the design rests on**: the layout leaves the mask cells (top round-1 column, one padding cell per
round-1 column, the G-block) unconstrained AND unreferenced (no `A_q/B_q/C_q` row, no chain/wide shift, no lookup
selector touches them) — checked by `zk.check_layout` (§6), a hard requirement on `layout.py`.

## 3. Layout requirements (for ligerito-sumcheck; `## IR requests`: none — this is layout, not IR)

* `layout.n`, the round-1 shape `(k_1, k'_1)` (from `params.py`) and a predicate/set of **constrained-or-referenced
  cells**; the cells `[N - 2^{k_1}, N)` and `{c . 2^{k_1} + q : c < C_1 - 1}` (with `q` chosen by the layout: a padding row)
  must be outside it. `zk.check_layout` verifies it with the layout's own `referenced_cells()` (or a dense mask).
* The zero-check's summand must vanish identically on unconstrained cells (constraints are *located* at cells and
  padding cells carry no constraint) — true for a Spartan-style `sum_q rho_q (A_q f)(x) (B_q f)(x) - (C_q f)(x)` with
  zero rows at padding cells; say so in `layout.py`.
* Chain-end / boundary constraints must not reference the cell after the last real column (the mask column may be its
  neighbour in the flat index).

## 4. Cost (rows / bytes / time), N = 2^29 (fp8-ada 4096 VUs), proto's dims `k' = (7,4,4,4)`, `|S| = 192`, `t_pad = 256`

| item | size | prover cost | proof bytes | 
|---|---|---|---|
| mask column (2^22 cells) | 0.78 % of cells; 0 extra if it is layout padding | 4.2 M ChaCha symbols (~1 ms on a 4090: `mask_sampler` does 1 M in the redteam probe), encode/hash unchanged in size | 0 |
| A-cells (127) + G-block (6(3n+1) = 528 cells at n = 29) | 0 | 0 | 0 |
| RS padding, round 1: 128 x 256 base | +0.006 % message symbols; NTT length unchanged (2^24 >= 2^22 + 256) | 32 K symbols | `ybar_1`: 256 ext = 6 KB |
| RS padding, rounds 2–4: 16 x 256 ext each | rate 0.2504 / 0.254 / 0.3125 -> `|S|` 192 / 194 / 214 for 2^-130.2 per round (unique decoding, `((1+rho)/2)^{|S|}`); or double round 4's codeword (2^13, rate 0.156, `|S| = 165`, paths +1 level): **smaller** than today | negligible | `ybar_2..4`: 18 KB; round 3 +2 rows (+1.5 KB); round 4 +22 rows (+8 KB) or -27 rows (-9 KB) with the doubled codeword |
| Libra mask | 3n + 1 = 88 ext coefficients | 4 ext evals x 88 per round (host, microseconds) | `G`, `v_g`: 48 B |
| coins (8c) | `K ~ 60` slots | 60 Blake2b | 60 x 32 B commitments + 60 x 64 B openings = 5.8 KB (not proof bytes in the interactive reading; `rounds.sequential_depth = K + 1`) |

Prediction: **+0–0.8 % cells, < 1 % prover time, +25–35 KB (~3 %) proof bytes** at 770 KB. To be measured on the pod (§7):
mask sampling at 2^22 + 32 K symbols; padded vs unpadded column encode (same NTT length); an end-to-end stub prover
(torch, N = 2^20–2^24) zk vs non-zk. The ≤ 5 % budget is met with room; the honest number goes in §7.

## 5. Negatives / the simulator test (what `zk_test.py` and the pod run check)

1. Toy end-to-end (N = 2^12–2^16, stub PCS + stub degree-3 zero-check, numpy/torch CPU): honest ZK proof verifies;
   tampered opened row / wrong `ybar` / wrong `v_g` / wrong final vector / a constraint violated -> rejected.
2. **Mask-free control is distinguishable**: two witnesses (real structured vs all-zero); without masks the final vector,
   the expected symbols, the evaluation claims and the opened rows differ with overwhelming statistics (constant rows -> constant
   opened values; the trivial witness gives `y_ell = 0`); with masks every component passes a two-sample chi-square (64
   bins) and the opened rows are uniform. Exact rank at toy size: the leak matrix (L2, L3, L4, L6 as functionals of the
   cells) restricted to the mask cells has the same rank as on all cells.
3. Simulator vs real prover under the real hash and real verify: honest `V` accepts both; `V*` equivocating at any slot
   -> identical public aborts, no opened row sent; statement-adaptive `V*` (pre-chosen `S_i`) accepted and masked;
   `PublicCheckVerifier` (aborts iff a public consistency check fails, G1) aborts in neither world.
4. `zk.check_layout` rejects a layout with a constraint on a mask cell.

## 6. Interface (`backends/direct/ligerito/zk.py`, head f8eee3e; numpy, torch lazily for the device sampler)

~~~python
# --- the real layout (ligerito-sumcheck's z (R, C), row bits low) --------------------------------------------------
RowMaskLayout(n_i, n_c, k_L, uniform_rows, product_rows, g_row, sumchecks=(("zc",30,2,True),("rows",12,2),("shift",18,2)), b=3)
default_row_mask_layout(n_i=12, n_c=18, k_L=10, m=3777, free_from=3977) -> RowMaskLayout   # fp8-ada: rows 4088..4095, (3773,3774,3775), 3776
lay.a = k_L - b               # column bits interleaved below the row bits;  lay.cells = 12 . 2^18;  lay.g_cells = 762
f_index(i, c, lay)            # x = (c mod 2^a) + 2^a i + 2^{a+n_i} (c >> a)      (numpy-broadcastable)
z_to_f(z, lay) -> f (R C,)    # numpy or torch: one transpose of the (2^{n_c-a}, R, 2^a) view (9.5 ms at 2^30 on the 4090)
permute_point(point (n_i+n_c, 6), lay)   # sumcheck-lane order (row bits first) -> PCS variable order for f = z_to_f(z)
fill_mask_rows(z, lay, device) -> RowMasks(g_coeffs: list[(n_coeffs, 6)], cells)   # in place: uniform rows, Libra row, m3 := m1 m2
libra_block_claim(lay, idx, gm, r) -> (cells (6 n_coeffs,) PCS indices, weights (6 n_coeffs, 6), value g(r))  # ONE sparse round-1 term
lay.zk_params(n, k1, kp1, t_pad=256) -> ZkParams(row_layout=True)      # for the padding / coin helpers below
zk_mode_rows(lay, t_pad, K) -> str ; omitted(zp) -> str ; zk_statement(zp, mode="interactive", private_operands=True) -> str

# --- sumcheck masks (sumcheck.py) ---------------------------------------------------------------------------------
EqSumcheckMask(n, d, coeffs (1 + dn [+ d^2], 6), tau (n, 6) in ROUND order, cross=True)     # zero-check (eq-weighted summand)
  .zk_sum() -> G (6,)                       # prover sends G; verifier's initial claim is rho . G instead of 0
  .message_pair(xs=(0,1,2)) -> (3, 3, 6)    # add rho x this to the bivariate opening message M[a][b] (mixed representation: pass through the same eval)
  .message(t, r_prefix, xs=(0,1,2)) -> (3, 6)   # add rho x this to q_t(0), q_t(1), q_t(2) for t >= 2 (q(inf) = second difference)
  .final_value(r) -> g(r) ; .claim_weights(r) -> (n_coeffs, 6, 6)      # verifier: final E (abc0 abc1 - abc2 + rho g(r)) = claim
SumcheckMask(zp, idx, coeffs)                # plain Libra (sum_x g = 2^n a_0 + 2^{n-1} sum g_i(1)) for the rows / shift sumchecks
  .total_sum() ; .round_values(j, r_prefix, xs) ; .final_value(r) ; .claim(r) -> BlockClaim

# --- PCS hooks (pcs.py), unchanged --------------------------------------------------------------------------------
pad_columns(zp, M (R, C) | (6, R, C), device) -> (message (R + t_pad, C), mu)      # per-column RS padding, coefficient basis
padding_combination(mu, rbar (C, 6)) -> ybar (t_pad, 6)                            # in the clear with the next root
row_check_rhs(zp, k, eta_s, ybar) -> (6,)                                          # verifier: <U_i[s,:], rbar> = <gen_s, y_i> + this
rate(zp, k, n_i) ; queries_for(zp, k, n_i, target_log2=None, levels=4, total_log2=-128)   # padded rate; union default (F1/F7)

# --- coins (8c) -----------------------------------------------------------------------------------------------------
coin_schedule(zp, kprimes) -> list[str] ; CommittedCoins(schedule) ; ProverCoins(stmt, schedule, commitments, verifier)
challenge_from(stmt, C, k, r_k, count, indices_n=None) ; verify_opening ; CoinOpeningError
EquivocatingCoins / AdversarialCoins / AbortingCoins   # malicious V* for the tests

# --- the toy geometry (zk_stub.py only: column blocks in a rows-HIGH layout) -----------------------------------------
ZkParams(n, k1, kp1, sumchecks, t_pad, mask_cols_high_log2=3, mask_cols_low_log2=0, n_c, product_rows) ; mask_cells ; sample_masks ; apply_masks ; check_layout
~~~

## 7. Measurements (pod `vy-ligerito-zk`, RTX 4090 24 GiB reference part; `zk_gpu_test.py`, JSON in `/tmp/ligerito_zk_*.json` on the laptop)

| item | value |
|---|---|
| **Real layout (fp8-ada shape, z (4096, 2^18) int32 on the device): 12 mask rows** | **3.1 M cells = 0.29 % of N; `fill_mask_rows` 0.72 ms = 0.42 % of today's 0.17 s Ligero prover, 0.14 % of the measured 0.525 s Ligerito PCS prover (proto FINAL, 2^30)**; `z_to_f` 9.5 ms (the relation lane builds `f` anyway; a transpose instead of a copy) |
| RS padding, all 4 levels (`t_pad = 256`, sample + `ybar` combination) | 4.6–5.1 ms (host numpy; limb-matmul combination) |
| Libra masks, 60 rounds (zc 30 + rows 12 + shift 18), host numpy | 18 ms (Python call overhead: ~0.3 ms/round; the arithmetic is microseconds) |
| coins (K = 93–94 slots: commit, open, derive) | 1.0 ms |
| **ZK total, real layout** | **≈ 25 ms = 15 % of 0.17 s (Ligero), 4.8 % of the measured 0.525 s Ligerito prover; the device part is 0.7 ms** |
| device sampler (`ligero/mask_sampler.py`, ChaCha20 + rejection) | 4.5 G symbols/s at ≥ 2^24 symbols; pooled chi-square over 4 × 2^20 draws passes (one 2^20 draw hit chi2(63) = 128 once in ~16 draws; the pooled test at 2^22 and 2^24 is 57–91 — red team: look at the first-call statistics) |
| **The §1.0 column-block geometry (measured before §1.0b, for the record)**: 9 full round-1 columns | k'_1 = 7: 7.0 % of cells, 18 ms device; k'_1 = 8: 3.5 %, 9 ms — infeasible in the real layout anyway (§1.0b) |
| `apply_masks` torch path / `uniform_symbols_device` bit-exact vs the host derivation | pass |

**Against the brief's "≤ 5 % rows/time":** rows 0.29 % ✓; time 0.7 ms device ✓ (0.4 %); the honest total including host-side
Python bookkeeping is 25 ms = 15 % of the 0.17 s Ligero prover / 4.8 % of the measured Ligerito prover — the 23 ms of host work is
the same class of constant overhead ligerito-proto lists as their item 1 (numpy per-round calls), not arithmetic; on the device or
batched it is < 1 ms. **Simulator test:** `zk_test.py` — real vs simulated (masked) two-sample chi-square `p ∈ [0.11, 0.94]` on all
10 transcript components, structured-vs-trivial witness `p ∈ [0.30, 0.99]`; mask-free: `p < 1e-17` on every component (final vector
`chi2 = 17830`, the trivial witness's final vector identically 0) — the mask-free proof is distinguished with advantage ≈ 1.

## For ligerito-relation — how to enable ZK, exactly, and what it costs

1. **Layout (with ligerito-sumcheck).** `lay = zk.default_row_mask_layout(n_i=12, n_c=18, k_L=<final k of your dims>, m=<committed rows>, free_from=m+200)`
   — or pick the rows yourself in a `RowMaskLayout`: 8 FREE rows covering every residue mod 8 (`4088..4095`), 3 COMMITTED rows
   `(i1, i2, i3)` and 1 COMMITTED row `g_row` touched by no constraint except the one you add: **one quadratic row `w(i1) · w(i2) = w(i3)`**
   in `sys.quadratic` (so `A` has a 1 at `(k*, i1)`, `B` at `(k*, i2)`, `C` at `(k*, i3)`). `build_z` must leave those 4 rows to the prover
   (they are witness rows with no Ligero producer); the 8 free rows are inside `w~` already (sumcheck lane §4: "part of the prover's z").
2. **Prover, per batch:** `z = build_z(...)`; `rm = zk.fill_mask_rows(z, lay, device)` (0.7 ms; BEFORE `sumcheck.prove` — the masks
   are witness cells); `f = zk.z_to_f(z, lay)` (replaces `f[i + R c] = z[i, c]`: the bit-interleaved table; 9.5 ms); commit `f`.
   Points: every `EvalClaim.point` from `sumcheck.verify` → `zk.permute_point(point, lay)` before handing it to the PCS.
3. **Sumchecks (needs ligerito-sumcheck's `cheat`/hook or a `zk=` argument in `prove`/`verify`):** zero-check: `gm = zk.EqSumcheckMask(30, 2,
   rm.g_coeffs[0], tau_in_round_order, cross=True)`; prover absorbs `G = gm.zk_sum()` right after `tau`, verifier draws `rho`
   (`challenge(b"zc/rho", 1)`), the prover adds `rho · gm.message_pair()` to the opening `M` and `rho · gm.message(t, r[:t])` to
   `q_t(0), q_t(1)` (and `q(inf)` = its second difference) for `t ≥ 2`; verifier: initial claim `rho · G` instead of 0, final check
   `E · (abc0 abc1 − abc2 + rho · g(r)) = claim` with `g(r)` = the block claim's value. Rows / shift: `zk.SumcheckMask(zp, 1|2, rm.g_coeffs[1|2])`,
   prover sends `G_k = .total_sum()`, verifier draws `rho_k`, add `rho_k · .round_values(j, r[:j])` to each round, final `+ rho_k g(r)`.
   Coin order: `G` before `rho`, `rho` before the first round message (`zk.coin_schedule` has the labels `zc/setup, zc/rho, ...`).
4. **PCS (needs ligerito-proto Phase B, two items):** (a) a **sparse round-1 term** `(column c*, rows, weights)` for the three block
   claims `zk.libra_block_claim(lay, k, gm_k, r_k)` — all 762 cells sit in relation columns `[0, 762)` of `g_row` = inside PCS column 0;
   batched with `alpha` like the eq/geom terms; (b) **per-column padding**: `msg, mu = zk.pad_columns(zp, M~_i, device)` before the
   encoder (message length `2^{k_i} + 256`; NTT length unchanged), `ybar_i = zk.padding_combination(mu, rbar_i)` in the proof, the
   verifier's row check adds `zk.row_check_rhs(zp, k_i, eta_s, ybar_i)`; `|S_i| = zk.queries_for(zp, k_i, n_i, levels=L)` with the
   padded rate (F1: fp8 L = 5 → `[240,173,174,176,194]`-class counts; `zp = lay.zk_params(30, k_1, k'_1)`).
5. **Shift claims (ligerito-sumcheck):** the three `w~(bits(c_x) || rho)` claims leak row `c_x` (§1.0b) — reduce them by a 12-round
   rows-type sumcheck at column point `rho` to one claim at an extension row point, with its own `SumcheckMask(("shift-rows", 12, 2))`
   (add the tuple to `lay.sumchecks`; +150 base cells in the Libra row). Until then ZK is NOT complete: state it in `omitted`.
6. **Coins:** live: `zk.coin_schedule` gives the K ≈ 93 slot labels (61 sumcheck + PCS + 3 `rho` + setup); `zk.CommittedCoins` /
   `ProverCoins` implement 8c over `transcript.LiveCoins`' slot stream (challenges are functions of `(stmt, H(c_1..c_K), k, r_k)` only).
7. **Fingerprint:** `relchain.zk_mode = zk.zk_mode_rows(lay, t_pad=256, K=len(schedule))`; `omitted = zk.omitted(zp)` (+ "shift claims
   unmasked" until item 5 lands); `zk_statement = zk.zk_statement(zp, "interactive", private_operands=<operands private?>)`.
8. **Cost:** cells +0.29 % (0 extra rows: 8 free + 4 of the spare committed rows); prover +0.7 ms device + ~25 ms host Python today;
   bytes: `ybar` 4 × 256 × 24 B = 24.6 KB + `G, rho`-related 3 × 24 B + `|S|` re-sizing per F1 (net ≈ −60 KB with the F1 counts vs pow2
   `[312,192,192,194,194]`, +25 KB `ybar`); coins +3 (`rho`s) + 1 (`G` is a prover message). Verifier: +3 block-claim evaluations
   (127 ext products), +`ybar` row-check terms (`t_pad` per opened row: 256 × |S| ext MACs per level — ~0.2 M, negligible).

## Discrepancies (D-style; the coordinator adds pointer stubs)

* **D-ZK1 (design vs layout, mine):** §1.0/§1.1 assumed relation rows are the HIGH PCS bits (a round-1 column = whole rows); the sumcheck
  lane's layout has rows LOW. Column-block masks are infeasible there (constrained cells in every PCS column; free rows only). Fixed in §1.0b
  (mask rows + interleaved index map); `ZkParams` column blocks remain for the toy only (`row_layout=True` disables them). Red team F6 = same finding.
* **D-ZK2 (sumcheck protocol as posted, ZK leak):** `values[1 + x] = w~(bits(c_x) || rho)` are bare functionals of the chain row `c_x`
  (boolean row coordinates) — 3 ext elements of witness information per proof. Owner ligerito-sumcheck; fix in `## For ligerito-relation` item 5.
* **D-ZK3 (red team F3, closed):** the separable Libra mask leaves the 9 cross coefficients of the bivariate opening round in the clear;
  `EqSumcheckMask` (eq-weighted, 2 × 2 cross block) closes it with the wire form unchanged — verified against brute force at n = 4.
* **D-ZK4 (F1/F7, closed on my side):** `queries_for` default is now the union rule `−128 − log2 L` at the padded rate; `params.py`/`LigeritoParams`
  still need `t_pad` (ligerito-pcs-fast).
* **D-ZK5 (cost claim vs brief):** "≤ 5 % time" holds for the device work (0.4 %) and for the total against the measured Ligerito prover (4.8 %),
  but the total against today's 0.17 s Ligero prover is 15 % — all host-side Python per-round overhead (18 ms Libra + 5 ms padding).
* **D-ZK6 (sampler):** one 2^20-symbol device draw gave chi2(63) = 128 (p ≈ 2e-6) once in ~16 draws; 2^22/2^24 draws and the host reference
  are normal (57–91). Not reproduced; flagged for red team (first-call / counter-start statistics of `mask_sampler.uniform`).

## FINAL (19:05Z) — lane ligerito-zk

**Branch `lane/ligerito-zk` head f8eee3e** (12 commits over e0cf2cd; `git status --short` empty; files: `backends/direct/ligerito/{zk.py, zk_stub.py,
zk_test.py, zk_gpu_test.py, __init__.py}` only; nothing under `ligero/` touched; no .md in the repo). Tests: 17 numpy (laptop 35 s, pod) + 5 device (pod) = 22 pass.

**Design in five sentences.** (1) Witness-side masking is 12 relation rows: 8 uniform rows in the free region whose residues mod 8, together with
`k_L − 3` column bits interleaved below the row bits in the PCS index (`x = (c mod 2^a) + 2^a i + 2^{a+12}(c >> a)`), make every entry of the
final vector, every fold entry, every column contraction and every fully-extension eval claim a functional of ≥ 6 uniform base cells with
F_p-spanning tensor weights — hence exactly uniform; 3 committed rows under the trivial constraint `m1 m2 = m3` mask the zero-check's `Az, Bz, Cz`
claims, and 1 committed row holds the Libra coefficients. (2) Opened rows are masked Ligero-style by 256 uniform RS-padding coefficients per
committed column at every level, with the padding combination `ybar_i` in the clear and the verifier's row check extended by it (rate and `|S_i|`
re-derived: F1). (3) Every sumcheck over witness tables (zero-check, rows, shift) gets its own Libra mask committed in the Libra row — for the
zero-check an eq-weighted mask with a 2 × 2 cross block so the bivariate opening round is blinded and Gruen's 3-value wire form survives — with
`G` sent, `rho` drawn, and `g(r)` delivered as one sparse round-1 PCS term. (4) All ~93 verifier messages are step-0 committed slots opened in
order, challenges are functions of `(stmt, H(commitments), k, r_k)` alone (8c), and the prover aborts publicly on a mismatched opening. (5) The
simulator rewinds `V*` after step 0, runs a dummy prover to learn the coins, re-solves the Libra coefficients and mask cells for the fake
witness so all public consistency checks hold, and re-runs the honest prover; its distance is the CRH/PRF terms plus the `O(1/p)` rank
event of the tensor weights. **Assumption it rests on:** the relation leaves the 12 rows unconstrained (except the trivial product row),
every eval claim the PCS receives is at a point with no boolean coordinate on the mask rows' bits (true after the shift-claim fix,
`## For ligerito-relation` item 5), and the PCS batches the 3 block claims as sparse round-1 terms.

**Measured cost (4090, fp8-ada shape N = 2^30):** cells +0.29 % (0 extra rows); `fill_mask_rows` 0.72 ms (0.4 % of 0.17 s); padding 5 ms +
Libra 18 ms + coins 1 ms host Python = total ≈ 25 ms = 15 % of today's 0.17 s Ligero prover, 4.8 % of the measured 0.525 s Ligerito PCS prover;
bytes ≈ +25 KB `ybar` − ~60 KB from F1's re-sized `|S|`; +3 coins. **Simulator test:** real vs simulated indistinguishable on all 10
transcript components (chi-square `p ∈ [0.11, 0.94]`); the mask-free proof is distinguished with `p < 1e-17` on every component.

**What red team should attack:** (a) the rank event — an adversarial `V*` choosing fold challenges with structure (all-equal coordinates,
base-field challenges, `r̄` with zeros) so the tensor weights on the 8 mask rows do NOT span F_{p^6} — the design's `1 − O(1/p)` is for uniform
challenges; with committed coins `V*` cannot pick them, so this is the coin-commitment binding; (b) the rows/shift sumchecks' final claims:
any claim at a point with a boolean coordinate on the mask rows' bits (`w~(bits(c_x) || rho)` today — D-ZK2); (c) the pad sub-batches: their
witnesses are public-ish (pad units), so `y_1` entries in rows `< m` of PCS columns 208–255 are functionals of KNOWN cells plus the witness —
make sure nothing else about `y_1` leaks (it is committed, only openings and folds are seen; the folds pass through mask rows); (d) the
equivocation abort: the prover's public abort at slot `k` reveals the prefix sent so far (by design, identical in both worlds — check the
prefix includes no unmasked message when `k` is the `rho` slot: `G` is sent before `rho`, and `G` is uniform); (e) the sampler first-call
statistics (D-ZK6); (f) the interleaved index map's interaction with proto's `Dims` (the final `k_L` must be ≥ 3 + the interleave; with
`k_L = 10..13` fine) and with the streaming-commit plan (row-major reads of `z` become strided).

**What integration still needs (owners):** ligerito-relation: items 1, 2, 7, 8 above (glue; ~40 lines). ligerito-sumcheck: a `zk=` hook adding
`rho · mask` to the round messages and `rho · G` / `rho · g(r)` to the verifier's chain (item 3), and the shift-claim reduction (item 5). ligerito-proto
(Phase B): the sparse round-1 term and per-column padding in `pcs.py` (item 4). ligerito-pcs-fast: `t_pad` in `LigeritoParams` (F1). Nothing
needs the coordinator except the decision on item 5 (without it ZK is incomplete and `omitted` must say so).
