---
cursor:
  subagentId: "bc-a2881cda-5857-5d2a-82bd-458f6b99d672"
---

lane: flock-soundness · kind: handoff · from: proximity-gap scoping (bc-a2881cda, a worker for the vllm Project coordinator) · created: 2026-09-27T16:55Z · repo: danielreuter/verity

# proximity-gap scoping → flock-soundness: A1 is provable from the ArkLib you already pin

Daniel asked me to scope how to remove A1 (`Assumptions.BCHKS25Thm46`). You own `table_sound`, so this comes to you before
anything is proposed to him. **Nothing in your development changes unless you agree.**

## The finding

- **ArkLib `b2e456fc` (your pin) proves Johnson-range MCA for Reed–Solomon codes over affine lines, in every characteristic:**
  `ReedSolomon.mcaError_affineLine_johnson_le`
  (`ArkLib/Data/CodingTheory/ReedSolomon/MutualCorrelatedAgreement/Johnson/Probability.lean`).
  - It is Dao–Kominers–Thaler, "Reed–Solomon Codes Beyond Johnson" ([ePrint 2026/2056](https://eprint.iacr.org/2026/2056)),
    ported by ArkLib's #907, which closed 2026-09-26.
  - I built it at the pin and ran `#print axioms`: `[propext, Classical.choice, Quot.sound]`. The same holds for
    `mcaError_affineLine_weightedJohnson_le`.
- **The statement.** For `domain : Fin n ↪ F`, `1 ≤ D ≤ n − 2`, `η > 0` and `a = √(D/n) + η ≤ 1`:

  ~~~lean
  mcaError (AffineLineGenerator F) (code domain (D + 1)) (1 - johnsonAgreement n D eta)
    ≤ min 1 (ENNReal.ofReal (johnsonExceptionCount n D ⌈johnsonAgreement n D eta * n⌉₊ eta / |F|))
  ~~~

  It uses the same `mcaError`, `AffineLineGenerator` and `ReedSolomon.code` as A1.
- **Its count.** `johnsonExceptionCount_lt_closed` gives $E_0 < \tfrac83\,n\,t'^3/\rho$, with $\rho = D/n$ and
  $t' = \max(\lceil\sqrt\rho/(2\eta)\rceil, 3) + \tfrac12$.

## Why it implies A1 (the Fin-domain instance, which is all Flock uses)

Take $k = D + 1$ and $\eta := 1 - \sqrt\rho - \delta > 0$, so the radius is A1's $\delta$ exactly. A1's
$m = \max(\lceil\sqrt\rho/\eta\rceil, 3) \ge m'$, so $t' \le m + \tfrac12$. With $(m + \tfrac12)^2 \ge 49/4$ and
$\rho \le 1$:

$$E_0 < \tfrac83\, n\, t'^3/\rho \;\le\; \tfrac23 (m+\tfrac12)^5\, n/\rho^{3/2} \;\le\; a .$$

- **The edge case $k = n$** (so $D = n - 1 > n - 2$): the code is all of $F^n$, so `mcaError = 0` (ArkLib's
  `mcaError_top_eq_zero`). $k > n$ contradicts $\delta < 1 - \sqrt{(k-1)/n}$.
- **Numerically,** $E_0$ is $2^{9.6}$ to $2^{12.2}$ below $a$ at every `fast100` level, and at most $0.09\,a$ over 200,000
  random points of A1's range (`internal/proximity-gap-formalization/`).

## What I would propose, for you to accept, change or take over

1. Prove `prCoin_mca_le` (and so `prCoin_level_mca_le` and the padded one) with no `hMCA`, for `Fin` domains, from the
   theorem above. The general-`ι` A1 would need a reindexing lemma for `mcaError`, which `prCoin_mca_le` does not use.
2. Drop the `hMCA` hypothesis from `table_sound*`, `table_sound_exec`, the compiled, knowledge, session and audit theorems.
   That is mechanical: about 115 occurrences in 20 files.
3. Keep the accounting as it is. `mcaA` stays BCHKS25's printed numerator, which the lemma above bounds, so every number
   is unchanged. Switching the term to $E_0$ later would gain about 10 bits on a term already below $2^{-170}$.
4. Update `ASSUMPTIONS.md` §3 and DESIGN.md §7. Both say A1 is "unproved in ArkLib, and not plannable", and that is no
   longer true at the pin. Table 1's `rs-proximity-johnson` would leave the assumption list.

**Not proposed:** any change to the protocol, the `fast100` schedule or M1. I also costed the unique-decoding alternative
Daniel asked about. On `fast100` at m = 33 it costs about 36% in proof bytes, and about 21% if levels at rate ≤ 1/8 use
ArkLib's proved 1.5-Johnson bound. It is moot unless you find a problem with the route above.

**Asks.** Tell me whether you object; whether you want to do (1)–(4) yourself, or want a proof-of-concept file from me
first; and whether you would rather keep `Assumptions.BCHKS25Thm46` as a proved theorem, with the reindexing, than
delete it. Reply by handoff in `internal/lanes/proximity-gap-scoping/` or to the coordinator. My write-up for Daniel is
`docs/proximity-gap-formalization.md`, and it says this is pending your review.
