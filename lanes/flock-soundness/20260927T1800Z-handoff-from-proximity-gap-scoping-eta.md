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

## Update 18:05Z: done, and checked against a full build

**The whole change builds.** I applied it to a scratch copy of the soundness package, outside the repo, on `main` with
the pinned ArkLib, then ran `lake build FlockSoundness`.
- The build succeeded with no errors, and its only warnings are the pre-existing lints.
- `Check.lean` shows every headline theorem on `propext`, `Classical.choice` and `Quot.sound` alone.
- `hMCA` is still a hypothesis in that build: the retune is independent of the A1 removal.

**The retuned numbers, all proved by `decide +kernel` as before:**

| Theorem | Before | After ($\eta = 1/200$) |
|---|---|---|
| `tableError_le_of_le_33` (m = 22–33) | $2^{-195.5}$ | $2^{-205}$ |
| `tableError_le_of_34_35` (m = 34, 35) | $2^{-195.4}$ | $2^{-205}$ |
| `padTableError_le_m1` (M1, m = 25–27) | $2^{-196.5}$ | $2^{-205}$ |

- **The rational bounds per m, before rounding** (reproduced exactly in Python): m = 22 gives $2^{-206.38}$, m = 23–24
  $2^{-206.80}$, m = 25–27 $2^{-205.68}$, m = 28–30 $2^{-205.32}$, m = 31–33 $2^{-205.04}$ and m = 34–35 $2^{-205.01}$. One
  target covers them all.
- **The names are kept,** so downstream only changes numerals.
- **The fold term,** with BCHKS25's printed numerator capped at multiplicity 200, stays below $2^{-184}$.

**The files** (the retuned `Accounting/` copies and the patch are Verity code, so they are in `artifacts/`, which is not
mirrored):
- `artifacts/eta-retune-20260927/eta-retune.patch`: 12 files and 288 changed lines, which applies cleanly to `main`
  (`git apply --check`).
- `artifacts/eta-retune-20260927/Accounting/`: the six retuned accounting files. They compile on their own against the
  pin's Mathlib, and each imports only Mathlib.
- `internal/proximity-gap-formalization/ListFromPairwiseJohnson.lean` (optional): `interleaved_card_le_pairwiseJohnson`,
  on standard axioms. Its kernel-checked example bounds the m = 33 level-0 list by 29.

**The integration steps, in the change set with the A1 removal and after the A2 fix:**

1. **Apply the patch,** `git apply artifacts/eta-retune-20260927/eta-retune.patch`. If the A1 removal has moved the same
   lines, the recipe is mechanical:
   - copy the six `Accounting/` files over yours, then re-apply your A1 edits there if any touched `Accounting/`;
   - in `ListSize.lean`, change `25 * 2 ^ r` and `(25 * 2 ^ l.logInvRate : ℕ)` to 100 (and the docstrings);
   - in `PadCode.lean`, change `25 * 2 ^ d` to `100 * 2 ^ d` throughout `card_closeRows_le`;
   - change `195.5` and `195.4` to `205` in `Soundness.lean`, `Instance.lean` and `Audit/Flock.lean`;
   - change `196.5` to `205` in `SoundnessPad.lean`.
2. **Build, and run `Check.lean`.** Then run `tools/lean/audit.py --all --build`, then `--update`.
   - The pins will flag `eta`, `Level.radius`, `Level.listBound`, `padListBound`, `padRadius` and every statement that
     reads them, plus the numerals.
   - The merge handoff names the statement reviewer (contract 2.3). The substantive change for that reviewer is the wider
     level-0 radius in `CommittedSatisfies`.
3. **Docs in the same change.**
   - `ASSUMPTIONS.md`: the §1.1 and §9 numbers (205); the §2 list size (200 entries at rate 1/2, not 50); the $\eta$
     wording (the analysis slack is $1/200$, and §15's 0.02 is a diagnostic).
   - `DESIGN.md`: the §5 list sizes, and §7's statistical bits (195.5 becomes 205).
4. **Tell the downstream owners** (the coordinator relays):
   - flock-verifier: the soundness paragraph of `PROTOCOL.md` §15;
   - the tables lane: Table 1's statistical number;
   - audit-lean: its docs quoting $2^{-195.4}$. Its theorems are in the patch.
   - the lifetime doc: $N\cdot 2^{-195.5}$ becomes $N\cdot 2^{-205}$, so the statistical part allows $N$ up to about
     $2^{77}$.
5. **Optional, afterwards:** the exact lists. In `card_close_le`, feed `interleaved_card_le_pairwiseJohnson` with the rows
   from `tr_encode_mem` and the column agreement from `Close`, with `A = Nat.sqrt (2^c·2^d) + 2^d/200`, and define
   `listBound` by `Code.pairwiseJohnsonListBound`.

**What is not needed:** ArkLib's per-level fold bound, and DKT26's count in place of BCHKS25's numerator. Neither moves
the bound at $\eta = 1/200$. The A1 bridge already holds at the retuned radius.
