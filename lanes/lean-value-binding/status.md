---
cursor:
  subagentId: "bc-a84aadb3-b06e-5db9-b0e4-e63614938d81"
---

# lean-value-binding: status

Agent bc-a84aadb3 (lane `lean-value-binding`, brief `internal/lane-briefs/lean-value-binding.md`). Newest first.

- **09:53Z Red-team conditions handled; waiting on TLO.**
  - #511 is in train TLO (with #520, #500, #490, #452). #513 at `655d509d` conflicts with `main` (RC 09:45Z). It gets
    `main` merged after TLO lands, a re-record, a recorded audit and fresh grants.
  - Prepared locally on #513's branch (not pushed): `eee9c27d`, C3 (fixed-address `row`/`salt`: `rowAt`, `saltAt`) and C2
    (the `δ_tree` caveat for bounds read from registered roots, in `ASSUMPTIONS.md`, the checklist and `Binding/E2E`). Also
    `3fc70517`, a merge of `main` `0cadbca3`.
  - [#526](https://github.com/danielreuter/verity/pull/526) (draft, `cursor/lean-per-prover-cr-8d81` @ `010b2c2d`, stacked
    on #513 and #514): **C1, A2 per prover.**
    - `LinkCR`/`linkBoundCR`; `flock_batched_linkSoundE` is now `LinkSound linkBoundCR`, with no A2 hypothesis.
    - Every `flock_e2e_*` (plus `_exec`, `UProg` and `_hm96`) takes `hCR` only at `(reg σ, cont σ)`.
    - `audit.py --update` PASS: 11,671 decls, 161 pins, 0 sorry.
    - Review request: `lanes/red-team-flock-3/20260930T0952Z-handoff-from-lean-value-binding-526-per-prover-review.md`.
    - Evidence: `evidence/per-prover-signature-diff.txt`, `evidence/per-prover-review.txt`.
  - Until #526 lands, cite the e2e bounds only as "if A2 holds for every prover's finder".
- **09:25Z** red-team-flock-3 granted #511 @`618ec5a5` and #513 @`655d509d`, both roles, with conditions C1 (both), C2
  and C3 (#513).
- **09:02Z** [#520](https://github.com/danielreuter/verity/pull/520): 2 MiB cap for `*/lean-audit.json`, in TLO.
- **08:57Z** recorded audits PASS: #511 `r20260930-082244-13e3` (148 pins), #513 `r20260930-082800-6e87` (159 pins), both
  labelled.
- **08:28Z / 08:05Z** #513 and #511 opened. **07:35Z** started; builds in `/workspace/research/trees/lean-value-binding{,-2}`
  on vy-nebius-1, CPUs 0-31.
