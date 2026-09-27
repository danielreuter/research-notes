---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

# PR #135 (core `IntegrityProfile`: log-space `rho`, one-pass `worst_case`): GRANT WITH CONDITIONS

Red-team review for the coordinator (request: `internal/lanes/red-team-flock-3/20260927T0810Z-handoff-from-coordinator.md`).
It covers PR #135 at head **b4c9a489** (branch `cursor/profile-exact-bound-f568`, base main **928790af**), and #121 at
1ed789d5 merged with it (merge commit 41d6e04b, local; clean). CPU only, in recorded run **r20260927-081834-33a0**.

Beside this file:

- `pr135_checks.py`: my checks. The exact reference is 60-digit `Decimal`, with my own LP: brute force up to 400 points,
  and above that an exact monotone-chain hull, which matches brute force on 300 random sets.
- `pr135_run_stdout.txt`: the run's output.

## Verdict

**GRANT WITH CONDITIONS.** The mathematics is right, and the underflow fix works. One condition, before merge:

- **P1: make the bound's rounding directed, so that `worst_case` is never below the exact LP optimum.**
  - **Today it can be below.** On my grid (400 profiles × 5 utilities, n ≤ 250), the new bound is below the exact
    optimum in 329 of 2,000 cases, by up to 8.7·10⁻¹² relative. It is below the old pairwise value by more than 10⁻¹² in
    6 cases, by up to 8.8·10⁻¹². At n = 4,000, k = 256, p = 1/2, 50 members, the new bound is 8.5·10⁻¹⁴ below exact,
    where the old one was exact.
  - **The cause is `rho`.** It computes log(den·C(n,k)) − log(a), which cancels two large logs when `rho` is small. The
    new `rho` overestimates, the optimistic direction, in 55% of 17,378 values, by up to 3.6·10⁻¹¹ relative. The old one
    was off by at most 3.3·10⁻¹³.
  - **The handoff understates it.** It gave "at most 6.6·10⁻¹⁵ relative"; I measure about 1,000× that.
  - **The practical effect is nil:** about 10⁻¹¹ relative slack in the bound, or equivalently in δ. But an audit's
    certified bound should err one way, and the fix is a few lines.
  - **Suggested fix:**
    - when `accept` ≥ 2⁻¹⁰⁰⁰, compute `rho` as `-log1p(-x)`, with x the exact 1 − `accept` converted to a float (correctly
      rounded from integers); keep the log difference only below that, where `rho` is large and the difference is
      accurate;
    - apply a relative margin far above the arithmetic's error: return the bound × (1 + 2⁻³⁰), or use `rho` × (1 − 2⁻³⁰);
    - pin a test against a high-precision reference that `worst_case` ≥ the exact optimum on a grid (my script can serve).

## The four checks

1. **The monotonicity behind the fast path: it holds, and the fast path doesn't depend on it.**
   - `accept(m) = 1 − p + p·C(n−m, k)/C(n, k)` never increases with m, for every law the profile admits (at most one
     Bernoulli p ∈ [0, 1], a `Subset` k ≤ n at the checked level). C(n−m, k) never increases with m.
   - `worst_case` sorts its points, (0, 0) and (rho(m), u(m)), before building the upper hull. So its value is the LP
     optimum for any order of the risks, and a non-monotone input can't give a smaller bound.
   - Evidence: I replaced `_rhos` with a shuffled sequence. For 5 utilities, `worst_case` equals a brute-force LP over the
     same risks (to within 10⁻⁹).
   - It doesn't refuse on non-monotone input, and it doesn't need to. On sorted input the sort is linear (Timsort), so
     "linear time" holds for real profiles.
   - `_rhos` updates C(n−m, k) exactly: C(N−1, k) = C(N, k)(N−k)/N is an exact integer division.
2. **Against the old pairwise calculation:**
   - The two are mathematically the same optimum. The old one enumerated the LP's vertices (single points, and pairs with
     both constraints tight); the new one reads the envelope at t = ln(1/δ)/members, scaled by members.
   - Numerically, the new bound is within −8.8·10⁻¹² … +6.0·10⁻¹¹ relative of the old one, and the error isn't directed
     (P1).
   - Which cases are zero agrees in all 2,000.
3. **The log-space `rho`:**
   - It doesn't underflow. At n = 4,000 and n = 20,000 (k = 256, p = 1) the old code raises `ValueError`, while the new
     bound is 5.9·10⁻¹⁵ and 5.6·10⁻¹⁵ above exact.
   - The A2 case, n = 183,680, k = 256, δ = 2⁻²⁰: new 9,675.419457199421 against exact 9,675.419457199405. That is
     +1.7·10⁻¹⁵, so the pinned 9,675.42 is right.
   - `inf` agrees with exact everywhere: `accept = 0` exactly when k > n − m and p = 1.
   - But it isn't directed at small `rho` (P1).
4. **Composition with #121** (1ed789d5 merged with b4c9a489, clean; tests 557 passed and 1 skipped):
   - `TOY` certifies 16.008 wrong RUs, or 64.03 VUs of work, against the adaptive attack's 16 RUs and 64 VUs.
   - #121's mixed class (4-VU and 8-VU RUs) is profiled from its units at n_v = 8, rate 1/8, and certifies 34.49 against
     the attack's 34.
   - My 750-point grid from the #121 review: the certified bound is never below the best adaptive attack, and never a
     whole RU above it.
   - Exact boundaries certify 10.0, 16.000000000000007 and 40.0.

## Tests

- #135 head: 540 passed, 1 skipped.
- Base: 525 passed.
- Merged with #121: 557 passed, 1 skipped.

The suites are `packages/verity/tests/proofs`, `protocols/sampled_proofs/tests`, `protocols/tests`, `tests/test_repository.py`,
`packages/verity/tests/test_boundaries.py`, `backends/flock/tests/test_audit_profile.py`, and vLLM's `test_challenge.py` on the
merged tree.
