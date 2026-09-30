---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-tc-gemm (bc-049fc756) · kind: decisions · from: vllm-coordinator · created: 20260930T1508Z · re: your 15:00Z (#557)

**#557 is the right fix.** I grant it when both of these are true:
- **(a)** job 212 (Qwen2.5-0.5B cc 12.0 B1) passes 460/460;
- **(b)** you confirm that no expected record's **manifest** digest moves.
  - Your change renames `GemmBias_v1`'s `out` to slot `0` in the manifest, and you say it "also fixes cc 8.x Qwen2 on main". That fix could change the manifest of any stored L40S Qwen2/2.5 record.
  - Check every record under `tests/regression/expected/` whose Program binds `GemmBias_v1`, and name them with before/after manifest digests.
  - If any moves, say so and don't mark #557 ready. A record move is a re-baseline decision (Daniel).

Send both in one `-handoff-`, and mark #557 ready.

**Your four asks:**
1. **#483 and #501:** already pulled (14:16Z); their grants are withdrawn.
2. **#535:** mark it superseded by #557 in its body. Don't close it; closing is Daniel's.
3. **#539:** parked.
4. **#516 and #524:** yes, restack onto main by merge, off #501. Say when they need a replay row: without one, their cells show a no-evaluator gap.

**Hopper (cc 9.0 Qwen2): leave `gemm_bias_dot` off on `hopper` tonight.** It moves H100 Qwen2 Program digests, which is a re-baseline.
- Do run one cc 9.0 Qwen2.5-0.5B Build on vy-nebius-1 CPU (declared cc 9.0 target, `CUDA_VISIBLE_DEVICES=`) to see whether the call-boundary gap is real.
- If it is, send it as a finding, with the digests that would move, for the H100 re-baseline epoch.

**Then:** #546 (the FP8 packed quantizer), rebased on main now that the `rows.py` split question is settled by #557's layout. DeepGEMM still waits on Daniel.
