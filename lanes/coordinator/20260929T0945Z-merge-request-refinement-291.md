---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T09:45Z · repo: danielreuter/verity · about: [#291](https://github.com/danielreuter/verity/pull/291), branch
`cursor/refinement-setup-cddd` at `2437e377`

# Merge request: #291, refinement R9c (both setups' statements are well formed), on `main` `610ee10f`

- **Hold for the red team's re-check.** Merging `main` changed `.lean` code outside my granted statements, so the red
  team was asked for a byte-identity re-check first (`red-team-flock-3/20260929T0945Z-handoff-from-refinement-r9c-r11-on-main-recheck.md`). No granted record moved: both packages' audits pass in
  compare mode.
- **Order:** after #278 (`20260929T0838Z-merge-request-refinement-278.md`). The branch contains #278's head `115fffc5`, #282's refusals and `main` `610ee10f`.
- **What:** `setup_wf`, `setupH_wf` and `stmtOf_linkLayout`, granted at `7003f003`. Their statements and records are
  unchanged.
- **What changed since `7003f003`:**
  - `main`'s merge. `Flock/HmRow.lean` conflicted: `pin` now takes both #345's and #282's refusals.
  - #282's refusals over `main`'s code. flock-soundness's `ExecCheck.check_facts` and `ExecSetup.pin_spec` get
    proof-only steps.
  - R9c's hm96 walk follows #345's typed `HmRow.parse`.
  The re-check note lists these file by file.
- **Build and audit:**
  - `lake build` of both packages succeeds. Audits PASS in compare mode: verifier 3,783 declarations and 15 pins; soundness
    9,377 declarations, 136 modules and 42 pins. Standard axioms.
  - `Refine/Setup.lean` still builds one theorem at a time (`Elab.async false`), about 6.5 minutes, and needs the
    memory noted in #291's first request.
- **`check`:** not recorded here. This VM has no evidence store, so please record one on `2437e377`.
