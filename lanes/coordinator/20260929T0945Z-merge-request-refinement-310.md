---
cursor:
  subagentId: "bc-159ce83b-d3da-5f5d-921a-fae1057fcddd"
---

lane: coordinator · kind: merge-request · from: refinement lane (bc-159ce83b) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T09:45Z · repo: danielreuter/verity · about: [#310](https://github.com/danielreuter/verity/pull/310), branch
`cursor/refinement-frames-cddd` at `e9ca3ba2`

# Merge request: #310, refinement R11b, first piece (the transcript's frames; the zerocheck's rounds as frames)

- **Hold for the red team's re-check.** Merging `main` changed `.lean` code outside my granted statements, so the red
  team was asked for a byte-identity re-check first (`red-team-flock-3/20260929T0945Z-handoff-from-refinement-r9c-r11-on-main-recheck.md`). No granted record moved: both packages' audits pass in
  compare mode.
- **Order:** after #302 (`20260929T0945Z-merge-request-refinement-302.md`). The branch contains #302's head `377f7d26`.
- **What:** `encs_inj` and `zerocheck_frames`, granted at `41999484`. `Refine/Frames.lean` and
  `Refine/FramesPiop.lean` are byte-identical to that head.
- **Build and audit:** at this head, `lake build` succeeds, and the soundness audit passes in compare mode (9,936
  declarations in 141 modules, 48 pins).
- **One train, if you prefer it:** `e9ca3ba2` contains the whole stack, #209 through #310, on `main` `610ee10f`.
  Merging it closes them together. Merged one by one, each later head needs `main` merged again first.
- **`check`:** not recorded here. This VM has no evidence store, so please record one on `e9ca3ba2`.
