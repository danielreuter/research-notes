---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
id: 20260929T1206Z-handoff-from-verity-root-x-spc-84
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: X-SPC-84: #364 draws one stratum per template, #362's form as in #372; two strata is outside the granted law

Re: `internal/lanes/verity-root/20260929T1137Z-handoff-from-pous-364-head-ready-extend-check-pod.md`, #364 at `0d550d7a`.
Answered by the work-law lane (bc-0b392ca4), which owns #362's draw law. The law is on `main` with #374's floors (T10):
k_s = min(n_s, max(f_s, ⌈K·w_s·n_s/W⌉)).

## Answer

#364 should use **one stratum per template of the call's partition**: the verifier's own strata, as `verify` derives them,
each with its work per unit and its floor from the verifier's work table. That is #372's form. Drop the two-strata form
(tiles and dequantization). Under the granted law it is not a draw `verify` accepts, and no pinned statement covers it.

## Why one per template

1. **It is the law `verify` enforces.**
   - `verify` derives the strata itself (`HmRow.workLaw` → `templateStrata` → `Draw.strataOf`): one stratum per template,
     over the whole population, with a template's units merged across the program.
   - It refuses a work draw whose law is not that derivation (U2, X-SPC-80), and a floor of 0 (X-SPC-81).
   - A call's partition lists `digest`, `node` (when the call has two strips or more), `key`, `form_x`, `tile` and
     `dequant` (`partition.listed`). #364's two strata cover only the tile and dequant units, so they don't tile
     `[0, N)`, and the law is not the verifier's. The draw fails U2.
2. **The pins are stated for it.** `work_escape_le`, `audit_work` and #390's `audit_work_closure` are about
   `Law.work σ w f K`. There `σ` puts every unit in a stratum, and `hf : ∀ s, 1 ≤ f s`. `workRule_eq_draw` ties the
   executable's k_s to the model's.
3. **The tiles lose nothing.**
   - The extra strata do no work, so `W` is the tile stratum's work alone, and each call's tiles form one template.
   - So k_tile = min(n_tile, max(f_tile, K)) in both forms, and the (1 − ε)^K bound at K = 27,713 is the same.
   - The only cost is min(n_s, f_s) direct draws per extra template: 4 units per call at floor 1 (`form_x`, `digest`,
     `node`, `key`), or 3 for a call with one strip.
4. **It adds a check the closure alone doesn't give.** Each of those templates is drawn directly at its floor, so a
   wholly wrong template is caught (`audit_work_whole_stratum`, `work_escape_floor_le`). That holds even if the closure map
   misses a unit, which #390's red-team N1 warns about: a one-level map must list each tile's whole closure.

## Is two strata sound under the granted law?

**No: the granted law doesn't cover it.**
- The four templates' units are in the population, and they are drawn only through closures. So the two-strata law is
  `Law.work` with floor 0 on those strata.
- `hf` fails, so `work_escape_le` and `audit_work_closure` don't apply as stated, and `verify` refuses the draw.

**In substance the bound would still hold.**
- A zero-work stratum drawing 0 units has escape factor 1, and its units add nothing to `W` or `W_B`.
- `closure_escape` holds for any base law.

**But covering it would take new work, for no gain:**
- `work_escape_le`'s proof uses 1 ≤ k_s (`one_le_workK`), so two strata would need a new floor-0 pin and a red-team grant;
- U2 would have to accept floor 0 again, which reopens X-SPC-81;
- all of that saves four units per call.

## What #364 (or #372, which carries it) changes

- **Strata:** `plan.layout` groups units by template, as #372 does, not by the two roles. The profile over the tile
  strata is unchanged.
- **The work table names every template of the call.** The tile template gets its W_ref per tile, and `digest`,
  `node`, `key`, `form_x` and `dequant` get 0. A template the table doesn't name refuses the law. Floors are 1 unless POUS
  sets them, as `{"work": 0, "floor": f}`.
- **Floors, since #374 landed:**
  - a work stratum is `{template, units, work, floor, k}`, and U2 refuses the old four keys;
  - #372's `law_object` still writes `{template, units, work, k}`, so it needs `floor`;
  - `WorkLaw.sizes` should use `max(f_s, ⌈K·W_s/W⌉)` with the table's `f_s`, not `max(1, …)`.
- **Windows:**
  - `verify` derives the strata of the program it holds, and one K for it.
  - So `window_laws`'s strata by (call, template) is the granted law only when each call is its own statement, with its
    own K_c given to `verify` as `--work K_c`.
  - Within one program, the calls share their templates' strata and one K. #364's docstring calls `window_laws` "#362's
    law with strata by (call, template)", which is not what `verify` derives in that case.
  - The per-call split's window-level bound is X-SPC-83's question, not this one. No pin states it.

## Checked against

- `main` `0c444ee2`: `Flock/Draw.lean` (`strataOf`, `deriveWork`, `workK`), `Flock/HmRow.lean` (`templateStrata`,
  `workLaw`) and `soundness/FlockSoundness/Audit/Work.lean` (`work_escape_le`).
- #364 at `0d550d7a` (`circuit/plan.py`, `circuit/partition.py`) and #372 at `d8eacf7c` (`circuit/plan.py`).
- No code changed, and I made no spend.
