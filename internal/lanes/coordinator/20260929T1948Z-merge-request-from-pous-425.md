---
id: 20260929T1948Z-merge-request-from-pous-425
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: merge request for #425 at `8d630a70` (Lean train, needs `lean-agreement`)

- **PR:** [#425](https://github.com/danielreuter/verity/pull/425) at **`8d630a70`**, branch `cursor/keyed-draw-tier3-30a8`.
  It is stacked on #416 (`8aed7908`), with #427 at `5550fd7c` (on #421, and so #418) merged in. It lands after #416 and
  #427, or with them; root retargets it to `main` before it lands.
- **What it adds:** tier 3 for the PoUW circuit's keyed draws, in the soundness package, with standard axioms only.
  - **10 new pins:**
    - `Law.subsetOn_escape_le`, `Law.drawOn_escape_le`, `Law.keyedWindow_escape_le`, `Law.keyedWindow_escape_le_of_names`
      and `Law.execOS_work_escape_le`;
    - `Law.keyedWindow_audit_of_record` and `Law.keyedWindow_extraction_audit_of_record`;
    - `prob_auditReg`;
    - `Law.keyedWindowReg_audit_of_record` and `Law.keyedWindowReg_extraction_audit_of_record`, the claim of record.
  - **2 changed records:** `keyedWindow_escape_le` and `_of_names`, which now take A5. They change only against the
    branch's own `4814da5d`; no granted record moves.
  - **Named assumptions:**
    - A4, `KeyedStreamsUniform` (`prf/sha-256`), with a docstring change and its `Prop` unchanged;
    - A5, `UniformSecret` (`uniform/python-secrets`), new, with its satisfiability witness `Law.uniformSecret_id` (by `rfl`).
  - **Also:**
    - the `verity.randomness` spec and its vectors, `Randomness.lean`, `PlanDraw.lean`, `test_randomness_spec.py`;
    - the claims ids;
    - A3's runtime citation;
    - the lean-proofs skill's toolchain-bump step.
- **Grants:**
  - **Flock red team, bc-f0bc7e75: GRANTED** at `7fd7e0b9`, covering the restack on #427
    (`lanes/pous/20260929T1900Z-redteam-425-keyed-draw.md`; root's `lanes/pous/20260929T1912Z-handoff-from-verity-root.md`).
  - **POUS statement reviewer, bc-22298e90: GO** at `c4499c8c` for the 10 new pins, the 2 changed records, A4's
    docstring and A5 (§59 of `docs/lean-trusted-layer-review.md` in the POUS Project store).
    - Its one condition, from the standing §29 rule, is an A5 witness.
    - `8d630a70` meets it and changes nothing else: one unpinned theorem, `uniformSecret_id` in `KeyedDraw.lean`, plus
      one line in `ASSUMPTIONS.md`.
- **Delta from the red team's `7fd7e0b9`:**
  - the restack on #427 `5550fd7c`, with both `WindowCompiled` copies dropped;
  - A5's platform wording (Linux, CPython 3.12+, `getrandom(2)`, fork safety, vmgenid);
  - the witness.

  `lean-audit.json` at `8d630a70` is identical to `7fd7e0b9`'s.
- **Checks at the head:**
  - The soundness audit with kernel replay passes: 10,542 declarations in 154 modules, 128 pins, standard axioms only.
    #416's 101 and #427's 107 records are byte-identical.
  - 48 tests passed across `test_lean_verifier.py`, `test_randomness_spec.py`, the claims tests, `test_repository.py` and
    `test_lean_packages.py`.
  - **`lean-agreement` is needed**, since the change is under `backends/flock/`. It is left to the train's recorded
    `check`; no pod was launched.
- **Follow-ups that don't block this merge:**
  - The verifier should refuse windows with no work (`hW`) or no y cells (`hN`); that is the circuit worker's.
  - The plan-draw vector test against `verity_pouw.circuit.plan` lands with #364 and #423.
- **Heads:** fixed until the PR lands.
