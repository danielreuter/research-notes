---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T07:52Z
---
# Overnight goal 8 (root-approved): the dropped rows as evidence only. Budget $60. Start after #23's Commit

Plan: `docs/overnight-plan.md`, goal 8. Daniel's morning sign-off should cover a whole epoch. Re-run the dropped rows at the
epoch tip **`101e8917`**, the same tree as #101/#67/#23, on right-sized pods, as **evidence only: no `rebaseline.py write`, no
commits to `expected/`**. Report per row: Build/Match/Commit status, program and manifest digests, run root, verdict, and every
check's result against the old `expected/` (the `rebaseline.py run --record` + `table` output is fine).

**Order (highest value first). Stop when $60 is spent or when the next row can't finish by about 16:00Z:**
1. **#75 (Qwen3-30B-A3B, TP2 MoE):** the only TP2 MoE row. Go through `tp_stage.sh`, and raise the rank Build timeout past 7200 s
   (it timed out at LP1024_T127). Use a 2x L40S host with a large RAM cgroup (check `memory.max`).
2. **#73 (Qwen3-4B bf16, H100 SXM):** the Hopper family. Its Commit OOM'd at 251 GB, so get an H100 SXM host with more RAM, or
   run the Commit with `VU_EXPORT=0` and the fixed admission bound. Skip it if no host with over 256 GB usable is in stock.
3. **#68 (OLMoE, arrivals):** the Build takes over 4.3 h, so start it early on an L40S pod with no memory limit (moe67 had none).
4. **#11 / #39 (B1 i4096 o512):** only if a host with at least 512 GB usable is in stock and budget remains (the planner puts #39's
   Build at 486 GiB). Otherwise record them as "capacity: needs ≥ 512 GB".
- **Skip #74** (the root: too slow).

**Rules:**
- Pods: `vyv-rf-epoch-g8-<row>`, registered with guard 90, bootstrapped from the tree, with `protocols/sampled_proofs` on
  PYTHONPATH (post-#29).
- Put `VU_EXPORT=0` on these memory-tight rows. The export is a different lane's goal.
- Check `memory.max` on every pod before launching, and use the fixed admission lag. Fixture keys follow `vllm-cloud-common.md`
  (mint on your VM).
- Checkpoint `WAIT ...` and end your turn while rows run. The vyv- deadline is 13:30Z now; the coordinator steps it to 16:45Z.
- vLLM has $127 left under the $770 cap, shared with vllm-more-exports ($30). **If project spend would pass about $760,
  stop.** The coordinator watches spend at every sweep.
- Report: a handoff "GOAL 8 epoch evidence" to `lanes/vllm-coordinator/`, and update READY.md's rows table (marked "evidence,
  not written").
