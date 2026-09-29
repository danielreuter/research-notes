---
id: 20260929T1933Z-report-keyed-draw-statement-425
campaign: verity
lane: pous
kind: report
status: open
repo: danielreuter/verity
origin: pous
---

# Statements for review: tier 3 for the PoUW circuit's keyed draws

**For:** the POUS statement reviewer and root's Flock red team (bc-f0bc7e75).
- **Branch:** `cursor/keyed-draw-tier3-30a8` at **`c4499c8c`**, stacked on #416 with #427 at `5550fd7c` (on #421, and
  so #418) merged in.
- **Printouts,** in the POUS Project store under `lean/submissions/sampled-proofs-influence/landing/`, reproducible
  with `python3 tools/lean/audit.py --update backends/flock/verifier/lean/soundness` at each head:
  - `review-keyed-draw-4814da5d.txt`: the chain's first five pins, against #416;
  - `review-keyed-draw-7fd7e0b9.txt`: step 4, A5 and the receipt-keyed game, against the merged tree;
  - `review-keyed-draw-c4499c8c.txt`: the delta since `7fd7e0b9`, which changes no record.
- **The audit** passes with the kernel replay: 10,541 declarations in 154 modules, 128 pins, standard axioms only. The
  records of #416 (101) and #427 (107) are byte-identical, and `lean-audit.json` is identical to `7fd7e0b9`'s.

## Since `7fd7e0b9`

- **Restacked on #427 at `5550fd7c`.** `Audit/WindowCompiled.lean` is gone. Its two lemmas,
  `extraction_audit_window_of_le_slack` and `extraction_audit_window_split_of_record_of_le_slack`, are now #427's in
  `Audit/Window.lean`, with the same statements, proofs and records. The red team reviews them in #427's delta.
- **A5's docstring and `ASSUMPTIONS.md` entry** carry the red team's wording (`lanes/pous/20260929T1817Z-redteam-423-receipt-key.md`,
  question 3), with no change to its `Prop`. The platform is Linux, with CPython 3.12 or later:
  - `secrets.token_bytes` reads `os.urandom`, which is `getrandom(2)`, blocking until the kernel's CSPRNG is initialized;
  - no user-space state, so a fork doesn't repeat output;
  - a VM snapshot restored more than once needs vmgenid reseeding (Linux 5.18 and later) or a hardware RNG;
  - the CSPRNG is idealized as exactly uniform, and the true bound carries its negligible advantage.
- **The per-strategy route stays** (`auditReg`, `prob_auditReg`). #429, root's receipt-indexed law, is parked as the
  fallback.

## Assumptions

- **A4 (`KeyedStreamsUniform`, `prf/sha-256`),** wording as the red team would grant it
  (`lanes/pous/20260929T1724Z-redteam-a4-keyed-streams.md`):
  - SHA-256's compression function is a PRF keyed by its chaining value (BCK96, on prefix-free inputs) and a dual PRF
    keyed by the secret bytes after a fixed public tag;
  - η is symbolic in Lean. `ASSUMPTIONS.md` states η ≤ 2⁻¹²⁸ at S = 32, with one η for every closure set, stream budget
    and receipt context.
- **A5 (`UniformSecret`, `uniform/python-secrets`), new, split out of A4:**
  - the window's secret is S uniform bytes, fresh for the window (#423's `secrets.token_bytes(32)`, C2);
  - `keyedWindow` now draws over the real secret source, with A5 as `hsec`.

## The chain (all pinned)

1. **The spec.** `Randomness.lean` (`verity.randomness` v1) and `PlanDraw.lean` (`plan.draw` and the window).
   - The spec reproduces `packages/verity/tests/randomness/vectors.json`.
   - Python matches the spec's vectors (`backends/flock/tests/test_randomness_spec.py`).
2. **`subsetOn_escape_le`:** `Key.subset`, one stream per swap, escapes ≤ the uniform `k`-subset.
3. **`drawOn_escape_le`:** C per-call draws form one `Law.stratified` over the window's strata.
4. **`keyedWindow_escape_le_of_names`:** on a uniform window secret (A5), under A4 for each `windowTest B`,
   `(keyedWindow sec …).escape B ≤ (Law.stratified σ k hk).escape B + η`.
   - A4's distinct framings come from admission and distinct stratum names (`frames_inj'`, `windowIdx_inj`).
   - `keyedWindow_escape_le` is the same with the distinct framings as a hypothesis.
   - Both records change at `7fd7e0b9`, since they now take A5.
5. **Step 4.**
   - `keyedWindow_audit_of_record` (oracle) and `keyedWindow_extraction_audit_of_record` (compiled) put it through
     #421's slack record form: the 0.1% event is at most `2^-40 + η + ε_ks + δ_link`.
   - The compiled layer goes through #427's `extraction_audit_window_split_of_record_of_le_slack`.
6. **The receipt-keyed draw, per strategy.**
   - `Audit/RegDraw.lean`'s `auditReg L session` is the game whose law depends on the registration.
   - `prob_auditReg` (`rfl`) moves each strategy to `audit (L (reg σ))`.
   - `keyedWindowReg_extraction_audit_of_record` is the claim of record, with `keyedWindowReg_audit_of_record` its
     oracle form. It is about `auditReg` at `ctx R`, the receipt digest (C1), with A4 and the analysis taken for every
     registration.
   - **The bound is instantiated at each receipt's own window structure.** The calls, `σ`, `w`, `v`, `f`, `cl`, `n` and
     `M` are parameters fixed before the game. A prover's claim is the theorem at the structure its own receipt lists,
     by the same per-strategy step.
   - **What the verifier must supply for each accepted receipt:** it derives `hWS`, `hnames`, `hsmall`, `hone` and `hfy`
     itself. Nothing checks `hW` (the window does some work) or `hN` (it has y cells) yet. The verifier should refuse
     windows that fail either, which is the circuit worker's follow-up (root, 19:16Z).

## Why per strategy, not a registration-indexed sibling

- The registration is a pure strategy's first move, fixed before the coin, so the real game's run is the fixed-law game's
  at `L (reg σ)`, definitionally. Every pinned theorem then applies unchanged.
- The new surface is one small game and one `rfl` lemma, plus hypotheses taken for every registration. No existing root
  pin changes.
- A registration-indexed sibling would need its own `Analysis`, `audit_profile` and window lemmas for an `R`-dependent
  law, which is more to review for the same bound.

## Grants

- **Flock red team (bc-f0bc7e75): GRANTED** at `7fd7e0b9`, covering the restack on #427
  (`lanes/pous/20260929T1900Z-redteam-425-keyed-draw.md`; root's `20260929T1912Z-handoff-from-verity-root.md`).
- **POUS statement reviewer (bc-22298e90):** requested at `c4499c8c`.

## Requested

A statement grant from each reviewer, at `c4499c8c`, for:
- A5, with its new wording;
- A4's docstring change;
- the 10 new pins that are #425's own: the five of the first printout, and in the second, step 4's two, `prob_auditReg`
  and the claim of record's two;
- the two changed records.

The other two pins of the second printout are #427's now, reviewed there.
