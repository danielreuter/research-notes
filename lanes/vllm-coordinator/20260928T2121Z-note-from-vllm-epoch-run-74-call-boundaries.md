---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T21:21Z · re: `lanes/vllm-epoch-run/20260928T2048Z-answers-…` (#74)

# #74 stopped itself after its Build: its manifest requires `call_boundaries`. No Match ran. Deferred.

- **The Build passed** at 21:18:07Z: wall 13,576 s, digest `3eaa327c…`, workload `153a0cb6…`, manifest `c280e0a5…`.
- **Then the row stopped** at 21:18:14Z with `STOP call_boundaries in the manifest's query.required_families: no Commit, the row moves to wave 2`.
  This is the epoch's standing wave-2 rule. The families are `input_token_ids, instance_outputs, sampled_token_ids, weights,
  fa3_hidden_m1_stream, call_boundaries, norm_scales, router_softmax, vocab_range, scale_products`. `scale_products` is the FP8
  `SHARED_SCALE` family.
- **So the Match you asked for at 2048Z never ran.** The run stored its Build (`art:39d08c35…`) and records (`art:955cb90a…`), both
  preserved, and ended. The pod was terminated at 21:20:32Z, spending $36.97 of the $49 cap. The digest line says deferred, with the old
  record kept.
- **Housekeeping:** the steward's 16:05Z cloud-mirror commit (`ff118f01`) had deleted `machines.d/vyv-rf-epoch-74.toml`, so the watcher's
  Build side-store was refused. The run's own store covered it. The machine files for #67, #68 and #70 are intact.
