---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: handoff · from: lean-organization · created: 2026-09-27T18:55Z · re: #130 merged

# #175 (upstream watch) is merge-ready; #149 (hardening) is ready for audit, with its `check` after #175

## #175: `cursor/lean-upstream-watch-68dc` at `7d67ed58`

- **Base:** retargeted to `main`, with `d69ce770` (train H) merged in cleanly.
- **check:** `r20260927-180833-e5a7` passed in 34 min (pytest 971 s, circuit-check 669 s, `lean-audit` 391 s; the agreement skipped). It is preserved.
- **Merge gate:** `research merge cursor/lean-upstream-watch-68dc --dry-run` from `main` answers: "may be merged".
- **Pins:** none change. The soundness policy only gains its `upstream` section, so lane contract §5 needs no statement reviewer.

## #149: `cursor/lean-audit-hardening-68dc` at `e1c588c3`

- **Base:** retargeted to `main`, with `d69ce770` merged in.
- **Passing:** all three packages pass `--build --update` in the sandbox (2,485, 832 and 4,335 declarations), and so do the 16 controls and 32 tests.
- **The re-record changes no statement.** A script comparison of the three policies shows every type hash, named assumption and read unchanged. Only the printed signatures lose their notation (11, 41 and 8 pins), and `dependencies` is new. Tell me if you still want a named reviewer for a notation-only diff under §5; the type hashes settle it, in my view.
- **New since you last looked:** the dependency digests now cover only the `.olean` files of the modules each package imports. The #175 exact pass built all of ArkLib here, and the old digest, which hashed every built file, would have changed with it. A PR that changes a package's imports now needs `--update`, and the failure message says so.
- **No `check` yet:** #149 and #175 overlap in `tools/lean/audit.py` and its README, and #175 adds the soundness policy's `upstream` section. So the plan is #175 first. Then I merge `main` into #149, keep both sides, re-run `--update` once, record `check`, and send you the head.
- **If you'd rather land #149 first,** say so, and I'll bring #175 onto it instead.

## Still open elsewhere

- **Soundness lane:** `soundness/ASSUMPTIONS.md` §3 still says A1 is "Unproved in ArkLib"; it should cite the computed status. `docs/lean-organization.md` §7 item 14.
- **Cache-key commit:** `cursor/agreement-key-policy-68dc` still waits for #134's rebase.
