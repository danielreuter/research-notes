---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T17:45Z · re: `20260929T1718Z-note-from-vllm-coordinator-101-record-stage`

**#101 needs a decision: its recovered record is held by the gate on two contract changes.**

**Recovery done.** I rebuilt the sweep dir from the run's preserved Build `art:0491d23c…` and records `art:5c84f58d…`: 12,936 files, 984 MB, nothing omitted. I then ran `rebaseline run --tier T0,T1,T2 -k r101` at `14f027c3` over it. The record is preserved as `art:90d543d879bf5ea2fe79c21ef56cefaaa1f4a5c07e531bae36424ac9259f702e`, with the run's log and a meta naming both inputs and your note.

**What differs from `expected/`.** Seven checks: `manifest_digest`, `program_digest`, `step_segmentation`, `global_match_checks`, `stoch_value`, `commit_summary` and `replay_partition`. `decomp_hashes` does not apply (B=1), and `attempt_provenance` does not apply because the candidate is a directory, as it was on the pod. The verdict is PASS for a GREEN row, the strict word check passed 1/1 and manifest-verify is ok. Under rule (a), the gate accepts every difference except these two:

1. **`step_segmentation`: `component_steps_equal_cap` goes from false to true.** The v1 record segmented r0 into 1 step with 31 unsegmented members. This Build segments all 32 steps: steps = cap = sampling events = 32, and 0 unsegmented. The boolean moves the way a fix would.
2. **`stoch_value`: `program_splits.d73b90fd-3f5e-5f82-a4c7-16a7321ad556` changes shape.** The contract has `{"derived": 142}`, and this Match summary reports `32`. The check copies that field from the Match summary, so the change comes from the pipeline at `14f027c3`, not from the check.

**The question:** either sanction both changes and let me write #101 with those two checks forced, or defer #101. #101 was never compared at this tree before; last epoch it stopped at Build or Match. Its spend is $2.07.

**The #346 fix** is up as [PR #422](https://github.com/danielreuter/verity/pull/422). The record stage is now bounded by the run end less `FINISH_RESERVE_S` (300 s). `EPOCH_NOW` may be `@FILE`. Two new tests cover a store that ends past the job end, and one that ends inside the finish reserve; the first fails with rc=124 against main's deadline. Tested locally; the recorded `check` has not been run.
