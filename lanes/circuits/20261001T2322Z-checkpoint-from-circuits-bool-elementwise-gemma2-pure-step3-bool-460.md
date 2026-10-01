---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T23:22Z

**Gemma-2-2B step 3 is done: 460/460 picks evaluated on bits on the Boolean IR, 460 equal to the committed outputs, 0 not, 0 not
evaluated, grade complete (`r20261001-200753-63d1`, run record `art:e0b6c08c…`, finished 3:49 PM PDT).** The word replay of the same
draw is 460/460 too, with linkage 32/32 and COMMIT PASS on both copies. The run used 12 workers under a 1,100 GB limit and peaked
near 713 GB; the Boolean grade took 2 h 37 min. PR branch `cursor/bool-gemma2-pure-8c79` @ `998ac159f` is merged with `main` @ `fa3c22edf`, which
took fb524e149's keep replay; the branch now adds only `kept_draw` and `boolean-replay`'s `outcome()` fixes (4 files, +86/−13), and
boundary-tree keeps still need 3d32e0733 on `main`. Body: store `internal/circuits/bool-gemma2-pure-pr-body.md`.
Two checks on the real keep, run at 4:50 PM PDT: at `998ac159f` the replay is refused by name before any pick (`r20261001-235008-4287`).
At `2f6d09ac3` (that head plus the draw port), it is 460/460 equal on words through `main`'s keep replay, COMMIT PASS (`r20261001-235024-61a2`).
