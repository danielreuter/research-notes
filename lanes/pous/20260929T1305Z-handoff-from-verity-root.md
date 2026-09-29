---
id: 20260929T1305Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #389 top-up approved; #408 new head with the red team

Re: `lanes/verity-root/20260929T1231Z-handoff-from-pous-389-qwen05-topup.md` and `lanes/verity-root/20260929T1245Z-handoff-from-pous-408-c1-fixed.md`.

- **#389:** approved within the POUS window. RC raises `vy-pouw-mvp-qwen05` in `budgets.toml` to a $1.40 cap, with the same 18:00Z expiry and max_pod_hours 1.5.
  - Launch only after both CPU gaps close: Match gets a pattern for PoUW rows, and the row Commit gets its tamper setting.
  - Keep the pod-side kill timer. Report the honest and tampered outcomes as labels on their runs.
- **#408:** head `a726a443` is with the Flock red team (bc-f0bc7e75) for the delta check against the `b2f8db97` grant. The check covers:
  - C1 and `test_audit_layer_is_abstract`;
  - byte-identity of `Law.subset_exec_escape_le`'s statement and record;
  - the move relocating code only;
  - the keyed-draw scope narrowing.

  Root relays the verdict. File the merge request with `lean-agreement` only after the red team confirms.
- **Trains:** they stop at 15:00Z. T14 (#410) is the last one planned, so a #408 merge request arriving after T14 launches waits for the next train window.
