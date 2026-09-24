---
lane: ligerito-sumcheck-3
kind: report
created: 2026-09-23T21:40Z
status: open
worktree: ~/projects/verity-main-wt/ligerito-sumcheck-3 (branch lane/ligerito-sumcheck-3 from lane/ligerito-sumcheck-2 @ 1fbbe86)
---

CHECKPOINT 26ff6af (23:08Z) [open] 19b5830: LGSC0004 default 13 coins/batch (zc 3,2,3,3,3,6/vf 10/cmb 6,6,6/rb 6,6): fp8-ada 4096 0.206 s 181,680 B, bf16-hopper 2048 0.197 s, 15/15 negatives each; soundness 184/|F| = 2^-177.9; toy fixture 1895b072 (+ zksmall fd8a264b); 52/52 tests; handoffs updated; next: big-table arity-3 kernel (12 coins)
CHECKPOINT ef49a7de (22:47Z) [open] ef49a7d: LGSC0004 coin-lean default 15 coins/batch (0.205 s, 164.8 KB at 4096 VUs fp8-ada 4090); zk-small 21 coins 0.154 s 15.8 KB; 51/51 tests; regenerating LGSC0004 fixture
CHECKPOINT f0b9567 (22:30Z) [open] f0b9567: LGSC0004 4096-VU fp8-ada ZK batch 0.155 s on the 4090 (LGSC0003 0.137 s at the same tip), 21 coins, 14.45 GB, 15/15 negatives reject; LGSC0004 toy fixture sha256 8c89da93 in evidence/; LGSC0003 fixture byte-identical to sumcheck-2's; writing argument + format note + handoffs next
CHECKPOINT c675bd5 (22:13Z) [open] c675bd5: LGSC0004 (ZK) implemented in layout.py/sumcheck.py -- Libra masks per round group (no extra coin), committed next rows + mask link + product triple, row reduction (+3 coins: 21/batch); 24/24 ZK tests + 20/20 LGSC0003 on the 4090; next: 4096-VU ZK timing, fixture, argument write-up
CHECKPOINT 3d5a731 (21:52Z) open — briefs, predecessor report + handoffs, ligerito-zk report, red-team FINALs read; worktree
created (predecessor has no commits after 1fbbe86). Took relation's fp4 `y_end` layout.py patch (3d5a731). Design for ZK on the
LGSC0003 round structure decided (LGSC0004, §1 below); implementing in sumcheck.py/layout.py next. Pod starting.

# ligerito-sumcheck-3 — ZK for the multi-variable rounds, coins, kernel floor

## 0. Findings before code

* **Rows <-> PCS round-1 merge (predecessor item 3) saves 0 coins in LGSC0003.** The combined sumcheck binds
  `n_cmb = max(n_i, n_c) = 18` variables because of the SHIFT part (over columns); the rows part (12 row variables) rides on the
  same challenges for free. Removing the rows part leaves the shift part's 18 variables = the same 6 coins. (The "~12 coins" was
  true for LGSC0002, where rows and shift were separate sumchecks.) Also, under ZK the PCS index map is `zk-interleaved`, whose
  top (round-1 wide) variables are COLUMN bits, not row bits.
* **LGSC0003 leaks more than the shift claims under ZK.** Besides `values[1 + x] = w~(bits(c_x), rho_c)` (D-ZK2), the final
  zero-check round sends `final_next[x][b] = next_x~(r_c_hi, b)`: 16 x n_links extension values that are bare functionals of the
  chain rows (next rows are virtual, no mask row reaches them). LGSC0002's `next_vals` had the same leak.
* **The ligerito-zk `EqSumcheckMask` does not transfer to multi-variable rounds** (red-team F3 in general form): a v-variable
  round message has 3^v − 1 free entries, including every cross term `X_j X_k`, `X_j^2 X_k`, …; a mask of `1 + dn` coefficients
  (one univariate per variable) leaves those cross entries as bare functionals of the witness. LGSC0004 masks every monomial.

## Interface (LGSC0004, posted 22:45Z at f0b9567) — `backends/direct/ligerito/{layout.py,sumcheck.py}`

LGSC0003 is unchanged (byte-identical fixture: sha256 019869b0… = sumcheck-2's). LGSC0004 is selected by the LAYOUT:
`lay = layout_for(sys, l, S, zk=True)` → `lay.zk` (`ZkRows`); `prove`/`verify` dispatch on `lay.zk is not None` (a format/layout
mismatch is rejected). New API, additive only:
* `layout_for(..., zk=True)`; `fill_zk(lay, z, key=None)` after `fill_z` of every sub-batch (samples U, g, i1, i2, M with the
  ChaCha20 `mask_sampler` under `key`, fresh `os.urandom` if None; sets i3 = i1·i2 and M_next = shift(M)); `lay.next_row(x)`.
* `prove(lay, cons, z, coins, cheat=None, engine=None, schedule=None)`: `schedule=None` on a ZK layout = `zk_default_schedule`
  (coin-lean, **13 coins** at the real size; zc 3,3,3,3,3,5 since 62f24d4, 23:17Z; 3,2,3,3,3,6 at 19b5830; 15 coins at
  ef49a7d); `_schedule_arg("zk-small", lay)` = the f0b9567 schedule
  (21 coins, fewest bytes); an LGSC0003 `Schedule` gets rb rounds added (`zk_schedule`); a full one with `rb` is used as is.
  `verify(...)` returns `(ok, reason, claims)` with claims =
  `[EvalClaim w(r_i, r_c), EvalClaim w(rho_i, rho_c), SparseClaim mask(zc), SparseClaim mask(cmb), SparseClaim mask(rb)]`.
* `SparseClaim(rows (T,), cols (T,), weights (T, 6), value (6,), name)`: `Σ_t weights[t] · w[rows[t], cols[t]] = value` over
  distinct base cells, all in `lay.zk.g_rows`. `check_claims(lay, z, claims)` checks both kinds against a witness.

ZK rows (fp8-ada, R = 4096, C = 2^18; all in the free region above the virtual block, which no longer contains `next:*`):
~~~
next     4079 4080 4081   committed next_x = shift(c_x)          (were virtual in LGSC0003)
mask     4082             M, uniform                              mask_next 4083: M_next = shift(M) (the mask link)
product  4084 4085 4086   i1, i2 uniform, i3 = i1 i2              constraint slot k_product = 3936: (i1:1)*(i2:1) = (i3:1)
g_rows   4087             Libra coefficients (first 6·coeffs cells: 24,072 default / 3,504 zk-small), rest uniform
                          (g_cells = 43,920 reserved = 6·122 per sumcheck variable, the arity-6 worst case; 7,200 at f0b9567)
uniform  4088 .. 4095     U, uniform: the SAME 8 rows as ligerito-zk's default_row_mask_layout (residues 0..7 mod 8)
~~~

Wire format (ext element = 6 × u32 LE, 24 B; message rep. `M[a_1]..[a_v]` exactly as LGSC0003):
~~~
"LGSC0004"                                    8 B magic
u8 Z, u8 zc_arity[Z]                          as LGSC0003 (default 3,3,3,3,3,5; zk-small 3,2,2,2,2,3,3,3,3,3)
u8 vf                                         (default 10; zk-small 4)
u8 n_links                                    (3 for fp8-ada; the mask link is NOT counted here)
u8 Q, u8 cmb_arity[Q]                         (default 6,6,6; zk-small 3 x 6)
u8 B, u8 rb_arity[B]                          row-reduction rounds, sum = n_i (default 6,6; zk-small 4,4,4)
zc_rounds[t]    3^{zc_arity[t]} ext           masked
final_abc       3 x 2^vf ext                  Az, Bz, Cz on the last vf variables (incl. the product slot)
T               1 ext                         the zero-check mask's final value K_zc
cmb_rounds[t]   3^{cmb_arity[t]} ext          masked
values          3 ext                         w~(r_i, r_c), V'(rho_c), K_cmb
rb_rounds[t]    3^{rb_arity[t]} ext           masked
values_b        2 ext                         w~(rho_i, rho_c), K_rb
~~~
Bytes: 8 + 1 + Z + 3 + Q + 1 + B + 24·(Σ3^zc + 3·2^vf + 1 + Σ3^cmb + 3 + Σ3^rb + 2); fp8-ada real N: **170,448 B** default,
15,800 B zk-small (LGSC0003 11,069). Parser: round arities 1..6 (`ZK_MAX_ARITY`; LGSC0003 stays 1..4), 1 ≤ vf ≤ 12
(`ZK_MAX_VF`) and vf ≤ n_c, sums = n_k + n_c (zc incl. vf), max(n_i, n_c) (cmb), n_i (rb, non-empty); n_links = the
layout's; 6·Σ(3^v − 1) ≤ g_cells; no trailing bytes; every coordinate < p. The default keeps vf ≤ n_c − 4 (ZK step 2 needs
≥ 12 cells per table entry); the parser does not enforce it (it is the prover's privacy, not the verifier's soundness).

Coins (labels as LGSC0003, header = the LGSC0004 header bytes):
~~~
absorb "lgsc/header" header;  tau = challenge("zc/tau", n)
for t < Z:  absorb "zc/q/{t}" M_t;  r = challenge("zc/r/{t}", zc_arity[t])
absorb "zc/final"  final_abc || T               (one (3·2^vf + 1) x 6 array)
ch = challenge("zc/final", vf + 3)              r_f, gamma, g3, beta as LGSC0003
for t < Q:  absorb "cmb/q/{t}" M_t;  r = challenge("cmb/r/{t}", cmb_arity[t])
absorb "values" values
for t < B:  absorb "rb/q/{t}" M_t;  r = challenge("rb/r/{t}", rb_arity[t])
absorb "values_b" values_b
~~~
Coins per batch = 1 + Z + 1 + Q + B = **13** default = 1 + 6 + 1 + 3 + 2 (zk-small 21; LGSC0003 18). Points: `r_var`, `r_c`, `r_k`, `rho`, `r_i`, `rho_c` as LGSC0003;
`rho_i` = the rb challenges reversed (n_i).

Verifier (L = n_links; `s_w = Σ_x g3^x e_{c_x} + g3^L e_M`, `n_w = Σ_x g3^x e_{next_x} + g3^L e_{M_next}`, R-vectors):
1. Zero-check rounds exactly as LGSC0003.
2. Final: `E · (Σ_b eq(tau[:vf], b)(abc0·abc1 − abc2)[b] + T) == claim`; A, B, C = MLEs of the tables at r_var[:vf].
3. Combined: claim = `beta · 2^(n_cmb−n_i) · 2^(n_cmb−n_c) · (A + gamma B + gamma^2 C)` (the shift part sums to 0: committed
   next rows); rounds `Σ_{b∈{0,1}^v} M_t[b] == claim`, claim = q_t(r).
4. Combined final: `2^(n_cmb−n_c) (beta coef(r_i) + n_w~(r_i)) z(r_i, r_c) − 2^(n_cmb−n_i) succ(rho_c, r_c) values[1] + values[2]
   == claim`, `z(r_i, r_c) = values[0] + Σ_{virtual rows v} eq(r_i, idx_v) pub_v~(r_c)` (no next_vals any more).
5. Row reduction: claim = values[1]; rounds `Σ_b M_t[b] == claim`; final `s_w~(rho_i) · values_b[0] + values_b[1] == claim`.
6. PCS: `w~(r_i || r_c) = values[0]`, `w~(rho_i || rho_c) = values_b[0]`, and the three sparse claims (`= T`, `= values[2]`,
   `= values_b[1]`), plus the V1 zero claims on `[m, m + len(lay.virt))`.

Sparse claim weights: mask j ∈ (zc, cmb, rb) has one group per message round (arity v), coefficients `c_{R,e}` for
`e ∈ {0,1,2}^v \ {0}` (row-major, e_1 = X_1 = the top remaining variable, most significant), groups in round order, masks
in the order zc, cmb, rb; coefficient u (global) = g-block cells `6u .. 6u+5` (cell k → `(g_rows[k // C], k % C)`), coordinate
d with weight `W_u · x^d`. `W_{R,e} = Π_j ev_j[e_j] − Π_j bw_j[e_j]`, `ev_j = (1, r_j, r_j^2)`, `bw_j = (1, tau_j, tau_j)` for
the zero-check (`tau_j = tau[nrem−1−j]`, the round's taus) or `(1, 1/2, 1/2)` for cmb/rb. fp8-ada default: 372 + 2184 +
1456 = 4012 coefficients (24,072 cells); zk-small 188 + 156 + 240 = 584 (3504 cells).

Fixtures (`~/.research/notes/lanes/ligerito-sumcheck-3/evidence/`; `python -m backends.direct.ligerito.sumcheck --zk --fixture
PATH [--schedule zk-small]` regenerates them), fp8-ada l = 64, S = 2, `LocalCoins(b"fixture")`, masks `sha256(b"fixture-masks")`:
~~~
lgsc0004_fixture_fp8-ada_l64_S2.json.gz          default: zc 3,5,4,4 / vf 3 / cmb 6,6 / rb 6,6   10 coins  81,093 B
                                                 JSON sha256 1895b0720b8d85d4864b708e3c18316979aab664be0ce9de20b43ea07fbd4778
lgsc0004_fixture_fp8-ada_l64_S2_zksmall.json.gz  zc 3×5 / vf 4 / cmb 3×4 / rb 4×3                 14 coins  12,985 B
                                                 JSON sha256 fd8a264b562d31d60e724d64cf2096af4b643ac0882300b803f1f4fa8572a62a
lgsc0004_..._f0b9567_obsolete.json.gz            the f0b9567 fixture (8c89da93…): same wire format, old layout
                                                 (g_cells 7200 moved every toy ZK row; verify-rs-3 c049225 verified it)
~~~
Same keys as LGSC0003's plus `layout.zk`, `schedule.rb`, `zk_g_cells` (the g block's first cells, so the sparse claims can
be checked without a PCS), claims with `kind` ("eval" | "sparse"; sparse: `rows, cols, weights, value`). 8 negatives each:
4 byte flips, "zc" and "all" cheats on a violated witness, M_next[0] += 1 (mask link), i3[9] += 1 (product row); each with
its Python reason.

## 1. ZK argument (LGSC0004)

Setting: the prover's randomness is U, M, i1, i2, the g block (all uniform, fresh per proof, independent of the witness); the
verifier is arbitrary (adaptive coins, live or Fiat–Shamir). Claim: everything LGSC0004 sends is simulatable from the public
data, given (a) the PCS is ZK for the claim set it is handed (two eval claims at points with extension row coordinates,
three sparse claims on g rows, the V1 zero claims) with U as its uniform rows, and (b) the rank events below.

1. **Round messages.** Round t of any of the three sumchecks sends `M_t = q_t + K_t·1 + L_t(g_t)`, where `q_t` is the honest
   (unmasked) message, `K_t` depends only on earlier groups, and `L_t(g_t) = mix(g_t) − base_t(g_t)·1` (times `2^{n_rest}`).
   `L_t` is an F-linear injection from the 3^v − 1 coefficients of g_t onto the hyperplane `H_t = {M : Σ_b w_t(b) M[b] = 0}`
   (`w_t = eq(tau_t, ·)` or 1): it is injective because a polynomial of degree ≤ 2 per variable with zero constant term that is
   constant is 0, and `dim H_t = 3^v − 1`. g_t is fresh when M_t is sent (it enters no earlier message and nothing else except
   the final K). So, conditioned on the whole past, M_t is uniform on the affine hyperplane of messages the verifier accepts
   in that round — whatever q_t is. The messages are therefore jointly independent of (witness, U, M, i1, i2).
2. **Final tables (zero-check).** Because (1) holds conditioned on i1, i2, those rows are still uniform given all messages.
   `Az(b) = A_w(b) + eq(r_k, k_prod) · i1~(r_c_hi, b)` etc.: each of the 2^vf entries of Az (Bz) is masked by a fresh
   extension functional of i1 (i2) over a disjoint set of 2^(n_c − vf) cells (fp8-ada: 2^8 = 256 with the default vf = 10,
   2^14 with zk-small's vf = 4) ⇒ uniform. Cz(b) is masked by `i3~ = Σ_c e_c i1_c i2_c`, which given i2 is a second
   functional of i1 with weights `e ∘ i2`, independent of Az's (12 ≤ 2^(n_c − vf) base dimensions: hence vf ≤ n_c − 4 in
   every schedule the prover picks) ⇒ (Az, Bz, Cz) uniform. T is then determined by the final check (it carries nothing
   more). Round arity does not enter steps 1-2: a round of arity 6 has 3^6 − 1 = 728 fresh coefficients for its 728 free
   message entries, exactly as a round of arity 3 has 26.
3. **values.** `w~(r_i, r_c)` contains `Σ_u eq(r_i, u) U~(u, r_c)`; U enters no message, table or constraint ⇒ uniform.
   `V'(rho_c) = Σ_x g3^x w~(c_x, rho_c) + g3^L M~(rho_c)`: M enters the combined messages only through q_t (masked, step 1)
   ⇒ M~(rho_c) is uniform given the messages ⇒ V' uniform (g3 ≠ 0). K_cmb is determined by the combined final check.
4. **values_b.** `w~(rho_i, rho_c)` contains `Σ_u eq(rho_i, u) U~(u, rho_c)`, a second functional of U, independent of the
   first unless the column points coincide ⇒ jointly uniform with values[0]. K_rb is determined by the rb final check.
5. **Sparse claims** reveal their values only (T, K_cmb, K_rb: already determined by the transcript).
6. **Simulator:** sample every message uniformly on its acceptance hyperplane in order (coins from the verifier), sample
   Az, Bz, Cz, values[0], values[1], values_b[0] uniformly, solve T, K_cmb, K_rb from the three final checks, and hand the
   claims to the PCS simulator. Identical distribution outside the rank events.
7. **Rank events** (statistical distance): `eq(r_k, k_prod) = 0` (≤ n_k/|F|), a deficient column-weight span for the table
   masks (needs 12 base dimensions per b: 2^8 cells at fp8-ada with the default, 2^14 with zk-small; the toy l = 64 has 16
   with its default vf = 3 and 8 with zk-small — the fixtures are format tests, not ZK instances), `r_c = rho_c`,
   degenerate i2: all ≤ 2^-150.
8. **The leaks of LGSC0003 are gone:** `final_next` is not sent (next rows are committed; the shift is proven inside the
   combined sumcheck through n_w); the per-link values `w~(c_x, rho_c)` are replaced by their g3-combination with the mask
   row M and reduced to a random row point (the row reduction); the cross terms of multi-variable rounds are masked (all
   monomials); Az, Bz, Cz are masked by the product triple.
9. **Differential evidence** (`sumcheck_zk_test.py`, 24 tests): two proofs with the same witness and coins but fresh masks
   differ in EVERY revealed element (every message entry, every table entry, every value), while LGSC0003 proofs are
   byte-identical under the same test (control); the sparse claims bind the committed coefficients (one flipped coefficient
   breaks exactly its claim); tampering any of zk_t / values / values_b is rejected.

Dependencies on the PCS (not this lane's code): U must be the PCS's uniform rows (it is: rows R−8..R−1), and the PCS's ZK
argument must count the two eval claims among its revealed U-functionals (ligerito-zk's "eval claims at fully-extension
points": it does) and accept sparse claims on g rows (proto `open(..., sparse=...)`).

## 2. Soundness (interactive, per batch; |F| = p^6, log2|F| = 185.44)

Per-round error of a v-variable round: 2v/|F| (Schwartz–Zippel on the degree-≤2-per-variable difference) plus, in the
zero-check, v/|F| for `eq(tau_j, r_j) = 0` (E would vanish and every later check pass: the predecessor's 127/|F| omitted it).
The masks add no term: `Σ_x w(x) ĝ(x) = 0` holds identically for ANY committed coefficients, the mask's final value goes to
the PCS as a sparse claim, and q + ĝ keeps degree ≤ 2 per variable.
~~~
                                                 zk-small (vf 4)        default (vf 10)
zero-check tau reduction                         n/|F|                  30/|F|                 30/|F|
zero-check message rounds (n − vf variables)     3(n − vf)/|F|          78/|F|  (26 vars)      60/|F|  (20 vars)
final tables at r_f (+ gamma: A, B, C)           (vf + 2)/|F|            6/|F|                 12/|F|
committed shift at r_c (next_x, M_next ≠ shift)  n_c/|F|                18/|F|                 18/|F|
g3 (degree L = 3 incl. the mask link), beta      (3 + 1)/|F|             4/|F|                  4/|F|
combined rounds (18 variables)                   2·18/|F|               36/|F|                 36/|F|
row reduction (12 variables)                     2·12/|F|               24/|F|                 24/|F|
total LGSC0004                                                          196/|F| = 2^-177.8     184/|F| = 2^-177.9
LGSC0003 recounted the same way                  (30 + 78 + 6 + 3 + 36)/|F| = 153/|F| = 2^-178.2   (reported 2^-178.4)
~~~
The sum depends only on how many variables each part covers, not on how they are grouped into rounds: a v-variable round
costs 2v/|F| (+ v/|F| for eq in the zero-check) whether v = 1 or 6. So the 8 coins the default saves cost no soundness; its
larger vf even helps slightly (a table variable costs 1/|F| against 3/|F| for a zero-check message variable).
(LGSC0003 has no shift-at-r_c term: its next rows exist only as `next_vals` at r_c, which the combined sumcheck equates to
the shift exactly. In LGSC0004 they are committed rows, so a wrong committed shift is caught only through D~(r_c).)
All ≥ 49 bits under the 2^-128 budget. Fiat–Shamir: ≈ Q · max per-round error: zk-small 9/|F| (zero-check arity 3) ⇒
Q ≤ 2^54 keeps 2^-128; default 18/|F| (zero-check arity 6) ⇒ Q ≤ 2^53. Under Fiat–Shamir coins cost nothing, so zk-small
(fewer bytes) is the better non-interactive choice; the default is for the live verifier. PCS claim batching (5 claims +
zero claims) is the PCS's term.

## 3. Timings (RTX 4090 reference pod, fp8-ada, 4096 VUs = one batch, N = 2^30, CUDA engine; warm median of 3)

~~~
                         LGSC0003 (f0b9567)   LGSC0004 c675bd5   LGSC0004 f0b9567
prove total              0.137 s              0.354 s            0.155 s
  zero-check             0.122                0.209              0.125
  combined (+ values)    0.016                0.086              0.026
  row reduction          -                    0.059              0.004
coins / bytes            18 / 11,069          21 / 15,800        21 / 15,800
peak GPU memory          14.45 GB             14.45 GB           14.45 GB
verify (Python, CPU)     0.52 s               0.63 s             0.72 s
fill_zk (witness side)   -                    0.080 s cold       (not in prove)
~~~
c675bd5 → f0b9567: the mask algebra (3^v × 6 tensors) was launch-bound — `fc_mul` is ~80 kernels; now a 4-op multiply
(`_fm`) on the CPU with the per-group base cached, and the rb tables use `_fm` too. ZK overhead now +18 ms (+13%): the extra
`z~(·, rho_c)` pass over z (~5 ms), mask messages (~0.4 ms/round), row reduction (4 ms). Negatives at 4096 VUs
(`--negatives`): quadratic / chain_link / lookup / zk_product / zk_mask_link × (honest, "zc", "all") = 15/15 rejected.
Evidence: `evidence/bench_lgsc000{3,4}_fp8-ada_4096*.json.gz`.

**Current tip (19b5830), LGSC0004 default = 13 coins** (same pod, warm median of 3; `--negatives` 15/15 rejected on both):
~~~
                         fp8-ada 4096 VUs                     bf16-hopper 2048 VUs (one batch; 4096 = 2 batches)
                         LGSC0003  zk-small   default 13c     LGSC0003  zk-small   default 13c
prove total              0.137 s   0.154 s    0.206 s         0.131 s   0.148 s    0.197 s
  zero-check             0.122     0.125      0.138           0.115     0.119      0.132
  combined (+ values)    0.016     0.026      0.062           0.016     0.026      0.060
  row reduction          -         0.004      0.006           -         0.004      0.006
coins / bytes            18/11,069 21/15,800  13/181,680      18/11,069 21/15,800  13/181,680
peak GPU memory          14.45 GB  14.45 GB   14.46 GB        14.22 GB  14.22 GB   14.23 GB
verify (Python, CPU)     0.52 s    0.72 s     0.71 s          0.58 s    0.62 s     0.61 s
~~~
bf16-hopper: its layout has the same N = 2^30 (n_k 12, n_c 18, n_i 12, m = 3196), but 4096 VUs need 25 sub-batches > S = 16,
so one batch holds 2048 VUs. The relation has no frozen tier in this tree: `instances(rel, n, seed=7)` is synthetic and
deterministic, generated on the pod (the campaign's `bf16-hopper-20260922-4096.npz`, sha256 4a2ec10c…, came with the
bootstrap but the sumcheck bench does not read it; timing does not depend on instance values). Evidence:
`evidence/bench_lgsc000{3,4}_bf16-hopper_2048*.json.gz` (`_v5` = 19b5830), `bench_lgsc0004_fp8-ada_4096_v5.json.gz`.

**Coins against prover time and bytes** (fp8-ada 4096, 4090, warm; "live" = prove + coins × 0.1 s RTT, sumcheck part
only; all verify, `--schedule` strings as given):
~~~
coins  schedule (zc / vf / cmb / rb)              prove     bytes     live@100ms
21     zk-small 3,2,2,2,2,3,3,3,3,3/4/3x6/4,4,4    0.154 s    15,800   2.25 s
15     3,2,2,2,2,3,6/10/3,3,6,6/6,6               0.169     164,834   1.67      (ef49a7d default, with the _fm tails)
14     3,2,3,3,3,6/10/3,3,6,6/6,6                 0.178     165,481   1.58
13     3,2,3,3,3,6/10/6,6,6/6,6    (default)      0.206     181,680   1.51
13     3,2,3,3,3,4/12/6,6,6/6,6                   0.198     387,312   1.50
12     3,3,3,3,6/12/6,6,6/6,6                     0.261     402,647   1.46
12     3,2,3,4,6/12/6,6,6/6,6                     0.446     403,511   1.65      (arity 4 on a 2^22 table: flat path)
~~~
What a coin costs: an arity-3 round on the 2^27 table after the opening takes 77 ms (the generic `zc_red3` kernel;
arity 2 takes 33 ms), an arity-6 combined round on 2^18 cells ~29 ms, arity 6 on the zero-check's 2^16 cells ~8 ms. The
default takes every coin that costs < 40 ms and < 20 KB. The 12-coin schedule saves another ~45 ms of live time at
100 ms RTT but doubles the bytes and depends on the RTT; a faster big-table arity-3 kernel (§4) would make 12 coins cheap.
ef49a7d → 19b5830 also moved the flat tails (rounds of arity > 3, small tables) from `fc_mul` (~110 launches) to `_fm`
(4 ops; `_fm_big`, a rotate-and-accumulate form with 6 temporaries per element, above 2^15 ext): 15-coin schedule 0.205 →
0.169 s.
