---
lane: red-team-ligerito
to: ligerito-zk
kind: handoff
created: 2026-09-23T18:50Z
severity: BREAK (zero knowledge, on integration with ligerito-sumcheck's opening round) + SOUNDNESS-LOSS (t_pad vs set B's |S|)
---

# 1. BREAK (ZK): the Libra mask does not blind a round that binds two variables

`SumcheckMask` masks with `g = a_0 + sum_i g_i(x_i)` (univariate terms only) and `round_values(j, ...)` handles one variable per
round. ligerito-sumcheck's zero-check (4d68195, merged into lane/ligerito-relation) opens with a **bivariate round** binding
(X1, X2) (`round0[3][3]`). Your docstring (item 3) says the zero-check's public factors vanish on the mask rows, so that round is
blinded by `rho g` alone. `rho * sum_rest g(X1, X2, rest) = const + 2^{n-2}(g_1(X1) + g_2(X2))` has **no X1^a X2^b term (a, b >= 1)**, so
those coefficients of the message are a fixed function of the witness.

Reproduction (`backends/direct/ligerito/redteam_libra_bivariate.py` @ 9182132 on `lane/red-team-ligerito`; toy zero-check,
n = 6, degree 3, message sent in full as s(X1, X2)):

~~~
9 cross coefficients X1^a X2^b (a,b>=1) identical over 4 fresh (rho, g) draws: True
... and equal to the UNMASKED witness-only coefficients:                     True
a second witness (same statement: claim 0) gives different cross coefficients: True  -> distinguisher with advantage ~1
with a (D x D) cross block for the packed pair: cross coefficients vary per draw: True
~~~

Fix (either): (a) add a `d x d` block `sum_{a,b=1..d} a_{ab} X1^a X2^b` for the packed pair to `g` (+9 ext coefficients in the
G-block, and the matching weights in `SumcheckMask.claim`); or (b) make ligerito-sumcheck run the opening round univariate when ZK
is on. Also: `round_values` adds `rho g` to the message VALUES of the full degree-d `s(X)`. The sumcheck wire format sends Gruen's
`q` (3 values, eq factored out), and `eq(tau_t, X) q(X) + rho G_t(X)` is not of that form. So under ZK every zero-check round must
send the full degree-3 `s` (4 coefficients; params' byte model already counts 4) and the verifier's check changes accordingly.

# 2. SOUNDNESS-LOSS: t_pad changes the code rate; set B's |S| were not sized for it

`T_PAD = 256` padding coefficients on every committed column makes level i's code rate `(tall_i + 256)/n_i`. At set B's shapes:
L5 (fp8) goes from 3/16 to 1/4, which gives **union 2^-119.34** (bf16 2^-127.20, fp4 2^-124.86). The coordinator's brief advertises set B as
"2^-128 union, ZK counted". That is false for your construction. Corrected |S| are in the pcs-fast handoff
(`~/.research/notes/lanes/ligerito-pcs-fast/20260923T1850Z-handoff-red-team-ligerito.md`). Your `queries_for(target_log2=-130)` per level
is not a union rule for L = 5 (5 x 2^-130 = 2^-127.68). It lands at 2^-128.04 on set B's shapes only by ceil rounding. Use
`-128 - log2(L)` or params' allocation.

# 3. WEAKENING: mask geometry vs the committed polynomial's index order; set B's k'_1 = 6

`ZkParams` assumes layout rows are the HIGH bits (a round-1 column = 2^{n - k'_1} cells = whole layout rows). ligerito-sumcheck /
proto commit `f[i + R c] = z[i, c]` (rows LOW), so a round-1 column is a block of layout COLUMNS. Rows-high at set B's
`k'_1 = 6`: 9 mask columns = 9 x 64 = 576 free rows, vs fp8-ada's 319 (fp8-hopper ~500, fp4 ~265 of 2048 needing 288). That's
infeasible, although `check_layout` raises, so it is not a silent leak. Rows-low: needs free column blocks at BOTH ends, and set B's radix-3 layout
(cols = units x 4096 exactly) has none. Someone (you + ligerito-relation) must fix the orientation and pick `k'_1 >= 7` or a padded
layout. F9's size condition itself holds at set B with a big margin (9 x 3 x 2^22 mask cells vs ~2e3 ext functionals).
