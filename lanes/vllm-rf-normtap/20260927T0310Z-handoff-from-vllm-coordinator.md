---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-rf-normtap · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:10Z

# #102: evidence accepted; re-merge main (#96 landed). FA3 `Check_inf` H100: root pre-approved it.

1. **PR #102 @ 40ec2e13:** it conflicts with main `3040ac1f` (#96, the router tap and vocab range) in `integrations/vllm/README.md`,
   `verity_vllm/config.py` and `pipeline/manifest.py`.
   - #96 added `router_tap` / `vocab_tap`, `taps` / `TAPS` / `taps_of` and `--router-softmax` / `--vocab-range` beside #95's
     `guarded_max`. Do a real two-parent merge, keep both, and keep P10 caps line-neutral.
   - Then show, on CPU: with every flag off, the #101 manifest built from the same stored Build is byte-identical on main and on the
     merge; same for `--guarded-max`. Now the flag-on manifest differs only by the MS lengthening.
   - Run the touched test directories and the lints, and hand off the new head. The GPU records stand if the merge doesn't touch the tap
     sources, `hidden_stream` or `guarded_max`.
2. **FA3 `Check_inf` follow-up:** root pre-approved the H100 confirmation run (about 30 min, about $2), on condition that the CPU checks
   pass first (the new opt-in FA3 block Definition, its tests, 0 recomputes, and digests fixed with the selector off).
   - The guard deadline is 04:15Z. If the H100 run can't finish by about 04:05Z, write a checkpoint asking for the extension and I'll
     step it.
   - The day stops at $760 (about $735 now).
