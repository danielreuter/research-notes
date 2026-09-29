---
id: 20260929T1807Z-handoff-from-pous-425-keyed-draw-review
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (statement reviewer, and red-team-flock-3 bc-f0bc7e75; cc work-law lane bc-0b392ca4): #425, tier 3 for the PoUW keyed draws, for review

From POUS's Lean lane. Draft [#425](https://github.com/danielreuter/verity/pull/425), branch `cursor/keyed-draw-tier3-30a8`
at **`7fd7e0b9`**. It is stacked on #416 (`8aed7908`), with #421 (`dbd1050c`, on #418) merged in.

**Read this first:** the Project store's `lean/submissions/sampled-proofs-influence/landing/keyed-draw-statement.md`. The
audit printouts are beside it:
- `review-keyed-draw-4814da5d.txt`: the chain's first five pins, against #416;
- `review-keyed-draw-7fd7e0b9.txt`: step 4, A5 and the receipt-keyed game, against the merged tree.

## For review

1. **A5, `Assumptions.UniformSecret` (`uniform/python-secrets`), new.** It is split out of A4, as the A4 verdict asked. The
   window's secret is S uniform bytes, fresh for the window (#423's `secrets.token_bytes(32)`, C2). `keyedWindow` now draws
   over the real secret source and takes A5 as `hsec`.
2. **A4's docstring**, with no change to its `Prop`.
   - It now names SHA-256's compression function as a PRF keyed by its chaining value (BCK96, on prefix-free inputs) and
     as a dual PRF keyed by the secret bytes after the fixed public tag (28 bytes for `stream`, 37 for `derive`).
   - η stays symbolic in Lean. `ASSUMPTIONS.md` states η ≤ 2⁻¹²⁸ at S = 32, with one η for every closure set, stream
     budget and receipt context.
3. **The 12 new pins:**
   - `Law.subsetOn_escape_le`, `Law.drawOn_escape_le`, `Law.keyedWindow_escape_le` and
     `Law.keyedWindow_escape_le_of_names`;
   - `Law.execOS_work_escape_le`, the optional law form from the #416 verdict;
   - `extraction_audit_window_of_le_slack` and `extraction_audit_window_split_of_record_of_le_slack`, the compiled
     layer;
   - `Law.keyedWindow_audit_of_record` and `Law.keyedWindow_extraction_audit_of_record`, step 4;
   - `prob_auditReg`, the per-strategy move;
   - `Law.keyedWindowReg_audit_of_record` and `Law.keyedWindowReg_extraction_audit_of_record`, the claim of record on the
     receipt-keyed game.
4. **The 2 changed records:** `Law.keyedWindow_escape_le` and `Law.keyedWindow_escape_le_of_names`, against `4814da5d`.
   Both now take A5, and `keyedWindow` draws over the secret source.

## The receipt-keyed draw: per strategy

- `Audit/RegDraw.lean`'s `auditReg L session` is the game whose law depends on the registration.
- `prob_auditReg` shows by `rfl` that each of its strategies has the same outcome probabilities in `audit (L (reg σ))`,
  since the registration is a pure strategy's first move.
- The claim of record takes A4 and the extraction analysis for every registration, with one η for all of them. No
  existing root pin changes.

## For the work-law lane: the compiled-layer slack lemmas are already written

`extraction_audit_window_of_le_slack` and `extraction_audit_window_split_of_record_of_le_slack` are in #425's
`Audit/WindowCompiled.lean`. They have the same proofs as #421's oracle-layer forms, through `extraction_audit_le`, and
the audit layer's import boundary holds. Please don't duplicate them. If you'd rather they sit in `Audit/Window.lean`
beside #421's lemmas, moving them is a one-file change.

## Checks at `7fd7e0b9`

- **The audit, `audit.py --update`: PASS with kernel replay.** 10,541 declarations, 128 pins, standard axioms only.
- **Existing records:** #416's 101 and #421's 105 are byte-identical.
- **Tests:** 48 passed across `test_lean_verifier.py`, `test_randomness_spec.py`, the claims tests, `test_repository.py`
  and `test_lean_packages.py`.
- **The recorded `check` with `lean-agreement`** is left to the train's recorded check. No pod was launched.
