---
cursor:
  subagentId: "bc-a2881cda-5857-5d2a-82bd-458f6b99d672"
---

lane: flock-soundness · kind: handoff · from: proximity-gap scoping (bc-a2881cda) · created: 2026-09-27T18:00Z · repo: danielreuter/verity · about: the η retune Daniel asked for, after the A2 fix and with the A1 removal

# proximity-gap scoping → flock-soundness: the η retune is small (effort estimate; the Lean files follow)

Daniel wants the extra margin if it's easy: per table from $2^{-195.5}$ to about $2^{-205}$, at unchanged `fast100`
queries. It is easy.

**None of the three new ArkLib results is needed** (the exact list bound, the per-level fold bound, DKT26's
$\eta^{-3}$ count). With one global $\eta = 1/200$, the bound follows from:
- your existing Johnson list proof (the lists become $100\cdot 2^r$);
- BCHKS25's printed numerator, now a theorem through the A1 bridge (`A1FromDKT26.lean` holds at every radius);
- the row-union folds you have.

At $\eta = 1/200$ the fold term is below $2^{-185}$, so it doesn't matter. Using `Bound.lean`'s own terms, the worst case
over m = 22–35 is $2^{-205.0}$, and M1's padded tables go from $2^{-196.5}$ to about $2^{-205.8}$. The exact lists would
add 0.17 bit; they are optional (below).

## What changes in the table theorem

- **One semantic change.** The level-0 radius in `CommittedSatisfies` widens from $1-\sqrt\rho-1/50$ to
  $1-\sqrt\rho-1/200$ (0.2729 to 0.2879 at rate 1/2), so "the committed values" means codewords within the wider radius.
  - Every pinned statement that reads `sch.level₀.radius` or `padRadius` changes meaning slightly: `table_sound*`, the
    padded, compiled and knowledge theorems, and the audit instantiations.
  - So it needs the named statement reviewer.
  - Knowledge extraction then decodes over at most $L_0 = 200$ candidates rather than 50 (or 29 with the exact lists).
- **The numbers in the statements.** $2^{-195.5}$ and $2^{-195.4}$ become about $2^{-205}$ (exact targets to follow from the
  rational check), $2^{-196.5}$ becomes about $2^{-205.8}$, and the downstream $2^{-195.4}$ quotes in `Audit/Flock*` follow.
- **If the statement must not move:** retune levels ≥ 1 only, keeping level 0 at 1/50. That gives $2^{-200.0}$ (+4.5 bits),
  but it needs a per-level slack (a field on `Level`) instead of one constant, so it is more edits for half the gain.

## What is mechanical

- **`Accounting.eta := 1/200`.** `LigeritoDecode`, `LigeritoLevels` and `LigeritoMid` use only $\eta > 0$ and
  $1-\gamma = \sqrt\rho+\eta$; their proofs should need nothing, or at most a `norm_num` re-run.
- **`Level.listBound := 100 * 2 ^ logInvRate`** and **`padListBound := 100 * 2 ^ logLen / (2 ^ logCols + t)`**, with
  `ListSize.johnson_value` and `PadCode`'s `hval` re-proved. These are two-line `norm_num` facts, which I'll include.
- **The rational accounting.** In `Fast100.lean`, `queryUp` needs $1/50 \to 1/200$, and `mcaA_bounds` needs its
  multiplicity cap raised from 50 to 200 (hence $101/2 \to 401/2$). `Numbers.lean` and `PaddedNumbers.lean` need new
  targets, rechecked by `decide +kernel`. I'm writing these as standalone copies, checked against the pin, for you to
  apply as diffs.
- **A1.** The DKT26 bridge is already general in $\delta$, so the retune adds nothing to it.

**Size.** Outside `Accounting/`, about a dozen lines: one constant, two definitions, two short proofs and docstrings. The
accounting changes are drop-in. It fits one change set with the A1 removal. Suggested order: A2 fix → A1 removal → η
retune.

**Optional:** the exact list bound. It gives lists of 29 instead of 200 at level 0 for extraction, and +0.17 bit. Its
bridge replaces `irs_lambda_le_johnson_mds` in `ListSize`; I'll write it if time allows.
