---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-tp2-gpuless-build, cc @circuits · created: 2026-10-01T04:05Z

# OLMoE TP2 fails TP-12: its attention all-gathers are unreplayable collective sites with no stratum (the token-budget fix works elsewhere)

- **Your token-budget fix (`b642a4a4b`) works.** On the epoch run's tree `5bab849b`, these TP2 B1 256/32 rows each pass 460/460 summed over the ranks:
  - p047 Qwen3-4B, with run root `bd0177d9…`, equal to your run D;
  - p036 Mistral-7B, p104 Qwen2.5-7B, p092 Qwen2.5-1.5B and p024 Phi-3-mini;
  - and the head_dim-64 rows p000, p012, p004 and p016 pass too.
- **cov-p069 (OLMoE-1B-7B TP2 B1 256/32 greedy) fails closed** (`r20261001-035205-8343`). The GPU-less 2-rank Build passed. On both ranks:
  `cross-rank collective outputs (TP-12): coverage of the unreplayable collective sites incomplete -- sites without a stratum: AllGather2_v1:
  ['model.layers.0.self_attn.all_gather2', '…all_gather2_1', '…all_gather2_100', '…all_gather2_1023']` (the list is truncated in the message).
- **Reading:** at TP>1, vLLM's OLMoE attention all-gathers q and k across the ranks for its full-width q/k norm. Those `AllGather2_v1` outputs are
  collective sites that the TP-12 rule must cover, and no replay stratum covers them.
  - Qwen3 normalises q/k per head, with no gather, and passes.
  - Qwen3-30B-A3B (p081) is next and should show whether MoE itself matters.
- **Log:** on vy-nebius-1, `/workspace/jobs/cov/cov-p069/olmoe-1b-7b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager/commit.log`. The
  OLMoE TP2 B8 row (p073) will fail the same way unless you say otherwise, so I'm leaving it queued as a second data point.

**Update 05:10Z: both MoE models fail at TP2.**
- **p073, OLMoE TP2 B8** (`r20261001-044849-7480`): the same all-gather gap as p069.
  - The `k_norm` rows' input, `model.layers.*.self_attn.all_gather2_*/out`, has no committed identity, so replay picks miss an input (F-r16-13).
  - The C2 population doesn't reconcile with Q(P): `vus_outside_query` and `identities_without_rows` x2752 at those sites (R17-3).
- **p081, Qwen3-30B-A3B TP2 B1** (`r20261001-035925-4198`): a different gap.
  - The identity check finds the manifest's MoE blocks (`model.layers.*.mlp`) missing on all 32 steps, on both ranks.
  - So the sparse-MoE layers commit nothing at TP2.
  - Qwen3-4B (dense, the same attention) passes, so this is the MoE path, not attention.
- p085 (Qwen3-30B-A3B TP2 B8) is the last one queued, and will most likely fail the same way.
