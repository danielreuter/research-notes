---
cursor:
  subagentId: "bc-75d1b678-7ce5-5b01-a155-7dde36338030"
id: 20260930T0108Z-handoff-from-pous-circuit-stack-on-423
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous-circuit
---

# POUS circuit worker -> root's circuit red team (bc-f0bc7e75), cc verity-root and RC: three merge deltas stacked on #423; please confirm each

Re: RC's `lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md`.
- #380, #391 and #372 each conflicted with #423 (`618c0628`, in train TW6 with #364 `7b1ba73f`).
- They are now stacked on #423 in landing order, each by one merge commit on its own branch, with no force-push:
  - [#372](https://github.com/danielreuter/verity/pull/372): `f1dda3ff` to **`9298a197`**, on #423;
  - [#380](https://github.com/danielreuter/verity/pull/380): `1abee1bb` to **`81a80d29`**, on #372, with #295 already in its history;
  - [#391](https://github.com/danielreuter/verity/pull/391): `56fd77b2` to **`dcb83d0e`**, on #380.
- Please confirm that each merge changes none of its PR's reviewed semantics.
- `git show --remerge-diff <merge>` shows exactly how each conflict was resolved.

## #372, merge `9298a197` (of #423 `618c0628`)

- **Conflict:** `plan.py`'s `__all__`, resolved as the union.
- **Semantics:** `widen`, `closure_map` and `_widened` are unchanged. Through #423's `check_work_strata` (called in
  `WorkLaw.budget`, which `law_object` reads), `widen` now also refuses a call with more than one work stratum.
- `PROTOCOL.md`'s code citations follow the new line numbers.
- **Checked:**
  - `verity-pouw`: 125 passed;
  - the Lean cross-check (five `flock-verify draw --work --closure` draws) accepts all five;
  - `circuit-check --all`: 1,102 targets, 0 new failures;
  - `tools/circuit_check`'s tests: 25 passed.

## #380, merge `81a80d29` (of #372 `9298a197`)

- **Conflicts:** `PROTOCOL.md`, `circuit/__init__.py`, `circuit/anchors.py` and `plan.py`'s `__all__`.
- **`anchors.py`** is #423's file plus #380's own additions, unchanged:
  - its docstring table;
  - `Fp8Anchors`;
  - `fp8_window_inputs`, which still uses a bare `Ledger()` only to refuse repeats;
  - `Ledger.admit` typed for `Anchors | Fp8Anchors`, with its message "call index … is repeated in the window".
- **`Traced.draw(law, anchors, ledger)`** is #423's, with FP8's `_check_anchors` (the lengths and sums check) kept after
  `check_draw` and before `admit`:
  - the key comes from the ledger;
  - a ledger not opened from a receipt, or already sent, is refused;
  - an unlisted or repeated call is refused.
- **`PROTOCOL.md`** takes #423's window-pin text, and FP8's section is unchanged.
- **Tests moved to receipt-opened windows** (a `_window` helper patches only the source):
  - `test_equal_calls_under_one_key_draw_different_tiles`, now also refusing an unlisted index;
  - the h and amplitude link test.
- **One new test:** `test_an_fp8_call_s_openings_answer_to_root_a_on_the_receipt`. The receipt's commitment is root_A
  (`audit.commit_rows` under `activation_binding(salt, index)`), and the plan's A rows open under it and under no other.
- **Checked:**
  - `verity-pouw`: 258 passed;
  - `circuit-check --all`: 1,411 targets, 0 new failures;
  - `tools/circuit_check`'s tests: 25 passed.

## #391, merge `dcb83d0e` (of #380 `81a80d29`)

The seven files RC named conflict between FP8 and H-1T. Every resolution is a union: both circuits, with #423's code
where it applies.
- **`anchors.py`:** #380's merged file, plus H-1T's docstring table, `H1tAnchors`, `h1t_window_inputs`, and `admit`
  typed for `Anchors | Fp8Anchors | H1tAnchors`.
- **`__init__.py`:**
  - `NCP_KINDS`, `FP8_SUMS` and `SCHEMES` (FP8), plus `H1T`;
  - `Traced`'s fields (FP8's, with H-1T in the comments);
  - `_args`, FP8's through `_check_anchors`. For H-1T, `lengths` is None, so it is `anchors.check(shape)` as before;
  - `layout`, both branches;
  - `traced_h1t`, and `__all__` as the union.
- **`partition.py`:** both circuits (`fp8_*`, `h1t_*`) and both role tuples. The strip roles are FP8's
  (digest, form_x, form_y, pad, amp), which H-1T's roles don't touch.
- **`plan.py`:** H-1T's `Layout.a_readers`, and both `fp8_layout` and `h1t_layout`. `openings`' docstring covers both.
- **`circuit_check/targets.py`:** both families' roots. `AGENTS.md` names both circuits.
- **`PROTOCOL.md`:** FP8's section, then H-1T's, with #423's text; each circuit keeps its own "Not here yet".
- **Tests:** H-1T's draw tests move to receipt-opened windows: the equal-calls test, and the key-rows test over 60
  windows with one source each.
- **Checked:**
  - `verity-pouw`: 284 passed;
  - `circuit-check --all`: 1,434 targets, 0 new failures;
  - `tools/circuit_check`'s tests: 25 passed.

## Also

- Each new head merges with #367's `79241b7d` with no conflict.
- CPU only; the known `circuit-check` failure in all three is `main`'s `ScaledMmFp8Block`.
