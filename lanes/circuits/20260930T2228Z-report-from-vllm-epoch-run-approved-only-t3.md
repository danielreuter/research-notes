---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-09-30T22:28Z · on your 21:52Z, 21:54Z and 22:02Z handoffs

**Checkpoint:** 423 labelled: 94 pass, 20 fail, 309 unsupported (node-2 Commits apart: 0). Node 1: 5 Commits running, 19 waiting (4.8 GPU-h, no floor now); 3 Builds running, 0 waiting.

- **Approved items only (Daniel's rule):** the queue holds only the approved subsets. Each job carries `env.RESEARCH_QUESTION`, and its result's `ov.note` ends with `question: …` (Qwen2/2.5 on #557; top-p across batch; MoE). **I withdrew 25 unapproved filler deployments still at their Build** (Jobs deleted, listed in `grid_not_approved` with the other unapproved cells). Deployments whose Build had finished stay, as your step 1 (Commit-ready). 11 approved deployments are left to dispatch, plus the 4 Qwen2.5-7B ones below.
- **The 4 old-template Commits:** none is waiting now. All 12 of my waiting Commits on node 1 and the 4 `n2-build` ones render `config-run@c43dba74fa68`, so the 21:48Z ones have since started or moved. There's nothing to resubmit.
- **T3 candidate:** `/workspace/jobs/cov/t3-candidate/` on node 1 holds `build_command.sh` (the exact command, `row stage build <row> B0 HuggingFaceTB/SmolLM2-135M 93efa2f0 --config-run 1 --replay-k 460`, with every env the build task sets), `env.json` and `reference.json`. **Caveat:** no two-task Build of this row ran on node 1. The reference is k01's pass `r20260930-083205-087a` (config-run-row, one task, tree `2847317c`), with its Build's program digests step `53aa6ed2…` and request `6ea7c413…`. That tree is older than v1, so the digests may differ for code reasons. Say if you want a fresh node-1 Build of the row on v1 as the reference (CPU only, about 3 min).
- **Fix: Qwen2.5-7B's Builds all failed at bootstrap (rc 3):** "no checkpoints.json entry for case B7". `pod_bootstrap.sh` maps only B0 and B1 to repos, and the Qwen2.5-7B entry's role is a descriptive string. On the run branch (`b3a7fde2`), B7 now maps to `Qwen/Qwen2.5-7B` (same pinned revision `d1497293`); `test_pod_bootstrap.py` and the lints pass. The 4 approved 7B deployments (B1/B8 × greedy/top-p) are requeued at the head.
- **Node 2:** no node-2 Commit of mine has landed yet, and cov-g217's cross-node run is asked for (`20260930T2208Z-handoff-from-vllm-epoch-run-g217-first-on-node2.md`).
