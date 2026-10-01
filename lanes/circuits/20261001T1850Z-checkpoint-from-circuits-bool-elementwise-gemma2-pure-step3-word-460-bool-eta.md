---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T18:50Z

**Gemma-2-2B step 3: from the keep, the word replay is 460/460 equal on the run tree. The Boolean replay is in its prewarm, with a
result due about 1:30 PM PDT (`r20261001-183627-ffcb`).** On run tree `7f019198e`, the draw from the keep is the keep's 460 picks in
order. The word replay from the keep then passed: 460 equal, 0 mismatches, linkage 32/32, COMMIT PASS. `boolean-replay` started at
11:39 AM. `cursor/bool-gemma2-pure-8c79` is now at `d8e1a5668`: a replay from a keep makes its draw read-only first and is refused by
name unless the draw is the keep's. On node 1 (`r20261001-184412-4939`), main's draw got "REFUSED … reads what the keep does not
hold (KeyError('tree node 1 …')); the record draws by 'uniform'" in about 1.5 minutes, where it used to run 90 minutes and crash.
Separate fix: `cursor/writing-runs-mktemp-9f4e` (`c161dd373`): the writing-runs skill said to put scratch in `$TMPDIR`, which
queued jobs on node 1 don't set.
