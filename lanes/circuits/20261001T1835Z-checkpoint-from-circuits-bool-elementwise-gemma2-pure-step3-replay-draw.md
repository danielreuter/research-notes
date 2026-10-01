---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T18:35Z

**Gemma-2-2B step 3: the keep is sound, but main draws different picks from it. The Boolean replay is rerunning on a tree that
draws as the record did (11:34 AM PDT, `r20261001-183438-bf0d`).** This corrects my 11:10 AM checkpoint. The row's Commit ran on the
boundary tree, which has 3d32e0733 ("the replay's k units are a uniform draw from every unit"), so its record says `replay_draw:
uniform` (strata `all|…`). 3d32e0733 is not on main (still not at e221350fd): main's driver always stratifies by family. Replayed
under main, the keep's seed draws 460 other units, 0 in common with the keep's 460 (the plan-only draw in `r20261001-182450-9fd5`).
Main's first Embedding pick needs a tree node the keep never held, so the run stops before evaluating any pick. Under the row's own
tree, the same draw equals the keep's 460 picks in order, with 0 missing reads. The run tree `cursor/bool-gemma2-replay-tree-9f4e`
(7f019198e) is my branch plus a port of 3d32e0733's draw (driver and `c2_replay`; tests pass). The job checks the draw first, then
runs the word replay from the keep, then `boolean-replay` (about 90 minutes of prewarm). For the bool-llama32 lane: cov-l32-bool was
also committed on a boundary tree, so its keep replay on main should fail the same way. It needs 3d32e0733 on main, or the same port.
