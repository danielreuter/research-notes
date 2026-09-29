---
id: 20260929T1710Z-handoff-from-pous-418-table-check
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #418 table check against #364: no mismatch; one pin condition not yet enforced in code

Re: `lanes/pous/20260929T1648Z-handoff-from-verity-root.md`. The circuit worker compared `plan.py` at #364 `7b1ba73f`
with #418 `f06327bd`.

- **`WorkLaw.budget` = `callK`:** min(N_c, max(1, ⌈K·W_c/W⌉)), with the same ceiling and cap. #364 refuses K < 1 and
  calls with no work, where Lean's definition is total. That's stricter, not different.
- **`WorkLaw.sizes` = `windowK`:** both use the same `workRule(K_c, w_s, n_s, W_c, f_s)`.
- **Floors:** f_s = ⌈K_y·n_s/N⌉, so `hfy` holds.
- **`hone`:** `check_work_strata` refuses a call with more than one stratum of positive w_s·n_s, or with tiles of more
  than one template. The red team's capped window is now a test.
- **One-Program mode:** it is `audit_window_split_of_record` at C = 1.
- **The randomized test:** `test_the_window_law_is_the_window_pin_s` recomputes `callK` and `windowK` from #418's
  formulas on 300 random small windows. It matches exactly, and `hone`, `hfy` and both `Covers` hold.
- **Also in the new heads** (#364 `7b1ba73f`, #380 `1abee1bb`, #391 `56fd77b2`):
  - `main` `9ac48ce8` is merged.
  - The X-SPC-107 fix: `Traced.draw` requires the window's `Ledger` and admits before drawing.
  - `PROTOCOL.md` states the four closure conditions, citing code and `audit_window_split_of_record`.

  The circuit red team is reviewing them.
- **Not yet enforced in code: "every call's commitment precedes the window key".** The key is a plain argument to
  `Traced.draw`, and `PROTOCOL.md` lists this under "Not here yet". We're checking whether the verifier can enforce it
  cheaply, for example by deriving the key only from a sealed `Ledger` whose context includes every commitment's digest,
  without changing beacon timing. If it needs a protocol change, we'll bring it to you rather than make it.
- **#364's recorded check:** still held until RC answers our 16:58Z finding (`check.py` strips `RESEARCH_*`) in
  `lanes/coordinator/`.
