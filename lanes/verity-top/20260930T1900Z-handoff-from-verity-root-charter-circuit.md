---
id: 20260930T1900Z-handoff-from-verity-root-charter-circuit
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Charter: circuit (vLLM circuits, built and validated on GPU/CPU)

Replies to `note:20260930T1842Z-handoff-from-verity-top-charters`. State as of 19:00Z Sep 30.

- **Owner:** vLLM coordinator `bc-ecac3029-d77d-50d3-b80b-df419ba48ee1`. **Stays** on as subcoordinator.
- **Remit:** turn served vLLM deployments into Verity programs (Definitions, lowering, exports), and validate them. That covers coverage cells (460/460 replay), config runs (Build, Commit, replay), the sm_120/Hopper ports and the Build step's speed. It grants the vLLM parts of PRs; the research coordinator runs the merge trains.

## Workers
| lane | id | owns |
|---|---|---|
| vllm-epoch-run | `bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622` | follow-up epoch rows and coverage cells on vy-nebius-1 |
| Build speed-up | `bc-47d0a3ed-166c-5d3b-830d-892cdf106942` | build-v1/v2 (#558 encode-once, #522 manifest lock) |
| MoE store test | `bc-1555924a-47f5-51e6-a4b6-a95f0882285b` | #443 (manifest build-global speed-up) |
| vllm-sm120-tc-gemm, -attention, -kernels, -fp8-ckpt | tc-gemm bc-049fc756-e63b-5b43-af14-0e5a94a2422d; attention bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; kernels bc-1cdd7aa4-8d99-53e6-96d6-c05199ad69c6; fp8-ckpt bc-f23795f4-fb08-523a-a894-44ef03ab3ebd | sm_120 GEMM/bias (#557), FP8 CUTLASS (#582), attention, kernels |
| vllm-config-run-tp2 | bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847 | TP2 config run #499, `--replay-deferred` PR A (`cursor/replay-deferred-bundle-3847`), PR B (replay stage) |
| vllm-staging-bug | bc-6a0184ce-a700-5063-99a5-c5056d33c646 | SmolLM2+Gumbel staging fix (`cursor/warmup-seeded-plans-c646`) |

## Open items (**D** = needs Daniel)
- #557, #581 (after #250), #499 granted, in RC's queue.
- #582 waits on core stack #515 → #516 (core grants + `lean-agreement`).
- PR B (CPU replay stage) to land; then every config run splits into three tasks.
- 10 SmolLM2-135M Gumbel deployments held until the staging fix lands.
- **D:** close the pulled #483/#501 (cuBLASLt model; served linears use Triton)?
- **D (made):** `fp8_block_gemm: "cutlass"` on sm_120 block-FP8 was approved at 15:22Z.
- Deferred epoch rows: #39, #11, #67, #68, #75, #74.

## Hands to infra
- The three-task config-run layout (`lanes/nebius-infra/20260930T1732Z-handoff-from-vllm-config-run-tp2-replay-bundle-layout-and-stage-commands.md`): the Kueue templates, the persistent Triton/vLLM caches, and keeping the Commit's GPU hold to about 2 min.
- GPU idle alerts on coverage jobs (e.g. cov-g147).

## Where state lives
- Inbox `lanes/vllm-coordinator/`; worker lanes `lanes/vllm-*`.
- Plans in the verity-root store's `docs/`: `vllm-followup-epoch-plan.md`, `vllm-circuit-ground-truth.md`, `vllm-config-sweep-plan.md`, `build-optimization-plan.md` (copies on request).
- PRs #557, #581, #499, #582, #515, #516, #558, #443.
