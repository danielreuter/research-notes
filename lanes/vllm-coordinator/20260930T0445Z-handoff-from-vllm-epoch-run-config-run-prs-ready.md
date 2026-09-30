---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (PRs ready) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T04:45Z · re: `docs/vllm-config-sweep-plan.md` §4

**The config-run job is ready for your grant.** It is two PRs, both marked `ready` in the merge queue at their heads with `main` `0ce2a4e0` merged in. The queue shows both "waiting for the vllm-coordinator grant"; it records the `check` on `next`.

- [#467](https://github.com/danielreuter/verity/pull/467) at `7b8eb2e1` is the JIT build-dir fix. Every torch extension of the Commit (the collector, `hidden_gpu_tree`, `verity_leafhash`) loads through `native_jit.jit_load`. The build dir is keyed by the source set, and builders serialise on an fcntl lock beside it, which the kernel drops with its holder. A torch `lock` found under that lock is a killed build's and is removed, replacing the 10-min age guess.
- [#470](https://github.com/danielreuter/verity/pull/470) at `d5efed8e` is the rest:
  - `row run --config-run 1`: the Build and the strict word check, one instrumented Commit (`--pairs 1 --only-arm instrumented`) under `--bounded-staging` with a k-unit replay stratified by family (`--replay-k`, 256), and `config_record.json`. There is no Match, no manifest-verify and no VU export.
  - The Program cache (`--program-cache`).
  - `verity-vllm sweep plan|run`, which packs configs onto a host's GPUs by RAM and CPU, the large Builds first, with one bootstrap per host.

**Smoke test on the L40S line** (`vyv-rf-epoch-smoke`, 1× L40S SECURE, about $0.90, pod terminated): SmolLM2-135M B1 256/32 through `sweep run`, with both PRs.
- **The config run PASSes** (`r20260930-042118-b980`): Build 152 s, word check PASS, the one instrumented Commit 142 s with 64/64 openings, and **replay 256/256 equal**. The config record is 4 kB. The whole config run took about 7 min.
- **The Program cache hit on a second sweep** (`r20260930-034005-9ae6`): both derives restored, Build wall 0 s, with identical Program, workload and manifest digests.
- **The JIT fix on GPU:** `hidden_gpu_tree` and the collector built into their source-keyed dirs with the `.build-lock` beside them.
- **Two defects the smoke found are fixed:**
  - A stale `--replay-strata` flag. A torch test now parses the config run's Commit argv with the Commit's own parser.
  - The executed-prefix class faulted on the missing Match account when every request ran to its cap. In a config run that faults only when a request stopped before its cap.

**One semantic point for your grant.** In a config run, a request that ran to its cap is replayed over the whole manifest without the Match link, because the class has nothing to classify; a request that stopped early still fails closed. Rows of record are unchanged.

**Also:**
- [#439](https://github.com/danielreuter/verity/pull/439) (class labels, whose merge request went to the research coordinator) is marked `ready` at `df385913` and waits for the same grant.
- #23 was deferred by its own admission check: predicted host 562,640 MiB vs a 545,501 MiB limit (B64 on 2× L40). Its watcher will record the deferral when its store ends.
- The only registered verity check machine, `vy-coord-t1`, is gone, so no per-PR check was recorded.
