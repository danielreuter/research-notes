---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T03:45Z · re: `docs/vllm-config-sweep-plan.md` §4

The config-run job is up as two PRs; the recorded check has not run on either, and the smoke test is running. [#467](https://github.com/danielreuter/verity/pull/467) is the JIT build-dir fix: every torch extension of the Commit loads through `native_jit.jit_load`, with a source-keyed dir and an fcntl build lock. [#470](https://github.com/danielreuter/verity/pull/470) has the rest: `row run --config-run 1` (Build and the strict word check, one instrumented Commit under bounded staging, a k-unit family-stratified replay), `config_record.json`, the Program cache and `verity-vllm sweep plan|run`. The smoke run is `r20260930-034005-9ae6` on `vyv-rf-epoch-smoke` (1× L40S SECURE, under the `vyv-rf-epoch-` line, at most about $2.50): SmolLM2-135M B1 256/32 twice through `sweep run` with one Program cache, to show the config run end to end and the cache hit. #23's Commit was refused by its own admission check (predicted host 562,640 MiB vs a 545,501 MiB limit, B64 on 2× L40), so it will be deferred when its job ends.
