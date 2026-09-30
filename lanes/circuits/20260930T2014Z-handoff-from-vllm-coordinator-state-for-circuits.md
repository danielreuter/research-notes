---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
id: 20260930T2014Z-handoff-from-vllm-coordinator-state-for-circuits
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-coordinator (bc-ecac3029), now @old-circuits-and-proofs
---

# @old-circuits-and-proofs → @circuits (bc-b8aaadaa): full state at 2026-09-30T20:14Z

This answers `lanes/vllm-coordinator/20260930T1956Z-handoff-from-circuits-state-request.md`. I'm your advisor from now on. Tag @old-circuits-and-proofs in the notes (in a `-handoff-` filename, because my inbox only lists handoff/asks/reply files) or on Slack once the relay is live. I'm subscribed to #agent-coordination, top-level only.

## 1. Workers

Only the lanes I launched are mine to resume: **config-run-tp2, coverage-defs, moe-triage, red-team-vllm-semantics, staging-bug**. The others were launched by root or the user; I steer them through their folders.

| Lane | bc-id | Now | Branch / PR | Done looks like | After that |
|---|---|---|---|---|---|
| vllm-epoch-run (coverage sweep) | bc-75fd4007 | Running the sm_120 coverage grid. GO at 19:09Z: re-run #594's proof, release the 130 held deployments, grow the grid to about 740 | run branch `cursor/coverage-v0-2622` (your `d7b32933`); follow-ups PR #503 | the grid labelled on the dashboard (`ov.ws coverage`) | continuous; give it the next grid |
| vllm-config-run-tp2 | bc-35ab914e (**mine, running**) | The GPU/CPU split: PR A `--replay-deferred` + replay bundle, PR B `row stage replay` with whole-field weight openings | PR A `cursor/replay-deferred-bundle-3847` @ `15c0f8b9`; PR B `cursor/replay-on-cpu-3847` @ `96dfc94b`; **no PR numbers yet** | both merged; deferred mode live in the steward's three-task template; GPU hold down by the replay time (Phi-3-mini B8 about 16 min) | FINAL, or resume it for the 8 TP2 grid deployments' problems |
| vllm-sm120-tc-gemm | bc-049fc756 | The FP8 CUTLASS stack (#515 → #516 → #582, after #557), then the 7, growing to about 84, FP8 deployments | #557 (granted), #582 (draft), #515/#516/#523/#524, #546 (parked) | #557 plus the FP8 stack merged; FP8 deployments labelled | ongoing (NVFP4: #523/#524) |
| build-optimization | bc-47d0a3ed | Two priorities from me: (a) measure per-Build RSS vs the request, cores per phase and the admission bound, then right-size or parallelize (root 20:03Z); (b) the 4k-context request derive (16:39Z) and reuse per model (19:09Z) | no PRs yet | measurement table plus fix PR/template numbers; the 4k derive under the timeout | ongoing (not mine) |
| vllm-coverage-defs | bc-ea0126bf (mine) | **FINAL** at 16:56Z: the Gemma-2 gap list is closed (#551, #568, #569, #581 merged); SiluMul_v2 (#552), LayerNorm (#553) merged | — | — | resume for: the FA2 softcap Match fold (not needed for config runs), `RoPE_v2` (low), Pythia's partial rotary/erf-GELU/biases |
| vllm-staging-bug | bc-6a0184ce (mine) | **FINAL** 18:53Z: the root cause of the +256 B staging failure (the warm-up dropped the per-request seed) → #594, merged | — | — | — |
| red-team-vllm-semantics | bc-05c0bb3e (mine) | **FINAL** 10:39Z: 22 assumptions rated (1 holds, 19 conditions, 2 broken) | — | — | resume for the invariance sweeps and served-kernel spot checks in the postmortem's table |
| vllm-moe-triage | bc-8d3fb01d (mine) | **FINAL** 10:00Z: OLMoE was a counting bug → #528, merged | — | — | — |
| vllm-sm120-attention / kernels / fp8-ckpt | bc-366317cb / bc-1cdd7aa4 / bc-f23795f4 | all **FINAL** (root-launched) | — | — | — |

## 2. PRs and grants

I grant the vLLM part (`grant vllm-coordinator` store labels, pushed with `labels-sync --push-only`). Core, flock and `lean-agreement` grants belong to others. **Merged today:** #228, #443, #479, #481, #497, #499, #527, #528, #536, #551, #552, #553, #558, #561, #562, #563, #568, #569, #581, #594.

| PR | State / head | vLLM grant | Other needs | Train |
|---|---|---|---|---|
| #557 `GemmBias_v2` (the served biased linear; Hopper too) | open, `470cf59d` | **granted** 17:20Z | — | queued with RC (my 17:22Z merge request) |
| #250 MUFU → `verity.ml.mufu` (consolidation) | open, `19cf12bc` | **granted** 18:14Z | consolidation's own | queued |
| #531 clean-host suites | open (draft), `4936634c` | **granted** 10:38Z | `tools/check` owners | RC's |
| #582 FP8 blockwise v2 (sm_120, CUTLASS) | draft, `82545853` | **not yet** | carries #515/#516; conflicts with main and #557 | after #557, #515, #516 |
| #515 / #523 (core sm_120 FP8 and NVFP4 steps) | open, `72b64c2b` / `91d3f7a2` | n/a | **core grant plus `lean-agreement`** (they touch `backends/flock`) | not filed by me |
| #516 / #524 (vLLM FP8 no-swap, NVFP4 linear) | open, `f023b5ea` / `1cddbdd6` | not granted at these heads (restacked) | follow #515/#523 | after their cores |
| #503 epoch-run config-run follow-ups | draft, `b0b612e0` | **not granted** | must drop `b27ab8a0`'s Program-cache hunk (#536 does it) and merge main | when the lane sends the head |
| PR A / PR B (replay split) | branches only | not yet | PR A conflicted with main after #499 (told at 18:17Z) | after grant |
| #546 DeepGEMM packed quantizer | open (not draft), `51318a6e` | **parked; don't train** | — | — |
| #483, #501 | open (draft) | **grants withdrawn** 14:16Z | — | pulled (see 4) |
| #535, #539 | open (draft) | none | superseded by #557 / parked | — |
| #443, #594 | merged | — | — | — |

## 3. Promises owed

- **Daniel:**
  - the node-2 SSH runner yes (I asked infra to bring it, 19:09Z; POUS's terms accepted);
  - the extra CPU VM only if node 2 isn't enough, as a question through root (not asked);
  - the replay-off-GPU semantics are approved (variant 3, `weights_attest` with whole-field openings, which I OK'd at 18:17Z).
- **Top-level / root:**
  - a measured GPU-busy % once deferred replay is live (I estimated 85–95% held, 20–40% SM-busy);
  - the ETA I gave at 19:09Z: GPUs full about 20:00Z from the 130 Commit-only re-runs; the new grid's Builds must land from about 22:30Z;
  - build-optimization's measurement plus fix (root 20:03Z).
- **RC:** grants on new heads as they come: #582's stack (vLLM parts), #503, PR A/B, build-optimization's PRs, and re-grant #250 if it's rebased again. Everything I grant I also file as a `-handoff-` in `lanes/coordinator/`.
- **Steward (bc-fd19a2fe):**
  - the TP2 lane owes it the bundle layout and stage commands (sent 17:32Z; check);
  - the steward owes the engine-key-ordered GPU queue, the CPU queue (plus node 2 if approved) and the three-task template;
  - Build memory requests per class from build-optimization.
- **@proofs:** nothing open from me that I know of.
- **@infra (bc-17cc41f1):** my ask for node 2's CPU (19:09Z).
- **Other lanes:**
  - epoch-run: grant its heads; answer its findings;
  - tc-gemm: grants for the FP8 stack; decisions on the 7→84 FP8 deployments (made);
  - consolidation: re-grant #250 on rebase.
- **I maintain** `docs/semantic-assumptions.md` in the Verity root store (a copy is in `lanes/nebius-infra/semantic-assumptions.md` in the notes). The rating label is `semantic-assumption "<moniker>=<rating>"`. It's yours now, or tell me to keep it.

## 4. Pending decisions

- **#483/#501: recommend closing both as superseded by #557.** Closing is Daniel's call; I haven't asked. #535 is superseded too, and #539 parked.
  - **Why epoch-run's run branch carries them:** it was built at about 09:40Z with #483 + #501 pre-merged, to cover the Qwen2.5 deployments, before tc-gemm's 14:01Z finding. It was never rebuilt without them.
  - **What they touch:** they bind only on `blackwell_consumer` biased linears (the Qwen2/Qwen2.5 family). There, the replay mismatched 51/460 (`r20260930-133959-eed1`): the served path is Triton + bf16 bias, not cuBLASLt.
  - **What closing changes:** no passing deployment. Any Qwen2/2.5 deployment labelled from that branch is a fail from a wrong Definition, and must re-run on a branch with **#557 instead of #483/#501**. Tell epoch-run to swap them; I hadn't caught that its branch still carried them.
- **Daniel:** the node-2 SSH runner (via infra); the CPU VM (not asked).
- **Mine, now yours:**
  - #582's stack order;
  - #503's grant;
  - PR A/B's grants;
  - whether cc 9.0 H100 re-baselines are wanted (#557 moves H100 Qwen2 Program digests; no expected record binds them);
  - the top-p "option 1" proposal: commit the sampler's interior boundary values, so top-p is provable. That's for Daniel; tonight uses option 3, the raised `VERITY_QWORD_MAX_GATES`, labelled "not provable in practice".

## 5. Running work

- **Cluster:** epoch-run's Kueue jobs on vy-nebius-1's `circuits` share. That's the 130 formerly-held stochastic deployments (released on #594's proof) and the grid growth. It also includes tc-gemm's FP8 jobs and the TP2 lane's PR A smoke jobs. Nothing runs on RunPod (the `vy-sm120-` line is at $24.31 of $60, and `vyv-cov-` was never used).
- **My timer:** `vllm-sm120-sweep` (hourly). Each fire it reads new lane files, reviews PR heads, grants and files merge requests, checks spend, and writes a one-line checkpoint in `lanes/vllm-coordinator/`. I'll keep it firing as your advisor, and relay what lands. Say if you'd rather I stop it.
- **Idles if nobody watches:**
  - the epoch-run lane's queue top-up rule (it's instructed to keep 8+ Commit-ready deployments queued; check its 30-minute checkpoints);
  - grants on new heads (trains stop without them).

## 6. Plans

Copied unedited into `lanes/circuits/inherited/`: `vllm-followup-epoch-plan.md`, `vllm-circuit-ground-truth.md` (author bc-289e3cdc), `vllm-config-sweep-plan.md`, `build-optimization-plan.md` (author bc-47d0a3ed). I checked them for secrets, and every match was about model tokens. I couldn't reach your store (`/cursor/stores/bc-7f347b4b-…` isn't mounted here). Also worth reading: the root store's `docs/semantic-assumptions.md` (the copy in notes) and `docs/gpu-utilization-postmortem.md`.

## 7. Advice

**Do first:**
1. **Keep the GPUs full.** Confirm epoch-run released the 130 and holds 8+ Commit-ready in the queue.
2. **Get PR A/B landed** and the three-task template default, so GPUs aren't held for replay.
3. **Get build-optimization's measurement** (root 20:03Z), since CPU admission is the real limit.
4. **Tell epoch-run to swap #483/#501 → #557** in its run branch and re-run the Qwen2/2.5 deployments.

**Stop:**
- anything that re-runs already-passing deployments;
- more semantic-correspondence side quests (Match fold, RoPE_v2, DeepGEMM) until the grid is full;
- RunPod: node 1 is free.

**Habits:**
- Name every message `-handoff-`: inboxes list nothing else.
- Grant in the same turn you approve, and push `labels-sync`. Twice today an approval without a label held a train.
- Adopt the GitHub broker (`docs/github-broker-rollout.md`) if your pushes fail.
