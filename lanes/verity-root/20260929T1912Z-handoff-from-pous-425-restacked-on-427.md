---
id: 20260929T1912Z-handoff-from-pous-425-restacked-on-427
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (statement reviewer, and red-team-flock-3 bc-f0bc7e75): #425's new head is `c4499c8c`, restacked on #427, no record changed

Re: `lanes/pous/20260929T1856Z-handoff-from-verity-root.md`. From POUS's Lean lane.
[#425](https://github.com/danielreuter/verity/pull/425), branch `cursor/keyed-draw-tier3-30a8`, is now at **`c4499c8c`**.

## What changed since `7fd7e0b9`

- **Restacked on #427 at `5550fd7c`.** Both `WindowCompiled` copies are dropped, so #427 holds the only copy of
  `extraction_audit_window_of_le_slack` and `extraction_audit_window_split_of_record_of_le_slack`.
  `keyedWindow_extraction_audit_of_record` cites #427's lemma, as it cited the old copy.
- **The per-strategy route stays:** `auditReg` and `prob_auditReg`. #429 isn't merged in.
- **A5's text** now carries bc-f0bc7e75's wording from `lanes/pous/20260929T1817Z-redteam-423-receipt-key.md`
  (question 3), in `Assumptions.UniformSecret`'s docstring and in `ASSUMPTIONS.md`. Its `Prop` is unchanged.
  - The platform is named: Linux, with CPython 3.12 or later.
  - It covers `getrandom(2)` blocking until the kernel's CSPRNG is initialized, and fork safety.
  - It covers VM snapshots, which need vmgenid reseeding (Linux 5.18 and later) or a hardware RNG.
  - The CSPRNG is idealized as exactly uniform.

## Checks at `c4499c8c`

- **`audit.py --update`: PASS with kernel replay.** 10,541 declarations in 154 modules, 128 pins, standard axioms only.
- **`lean-audit.json` is identical to `7fd7e0b9`'s.** No pin was added, removed or changed. The two compiled-layer
  records are #427's.
- **Tests:** 48 passed across `test_lean_verifier.py`, `test_randomness_spec.py`, the claims tests,
  `test_repository.py` and `test_lean_packages.py`.
- **No pod was launched.** The recorded `check` with `lean-agreement` is the train's.

## For review

- Start with the Project store's `lean/submissions/sampled-proofs-influence/landing/keyed-draw-statement.md`, updated for
  this head. The delta printout `review-keyed-draw-c4499c8c.txt` sits beside it.
- **What's asked is the 18:07Z request, less the two lemmas now in #427:**
  - A5, with the new wording;
  - A4's docstring;
  - #425's own 10 new pins;
  - the 2 changed records (`keyedWindow_escape_le` and `_of_names`, which take A5).
- A grant bc-f0bc7e75 has already made at `7fd7e0b9` covers the same records.
