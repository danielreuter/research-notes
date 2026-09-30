---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: build-optimization (bc-47d0a3ed) · kind: handoff (PRIORITY, sharpens my 19:09Z ask) · from: vllm-coordinator · created: 2026-09-30T20:03Z

# Node 1's CPUs are 71% idle, yet Builds are "the bottleneck": measure why, then fix admission or the derive

Root's reading: the limit isn't cores. It's either **Build admission**, where the `deployments-cpu` queue's memory quota admits few Builds because each requests far more RAM than it uses, or **single-threaded derives**, where one Build holds its slot while using about 1 core.

**Measure first, on the vLLM deployment Builds running now on node 1** (Kueue CPU queue plus direct runs), for about 10 Builds across small, 7B and batch-8 1k shapes. For each Build, record:
- **peak RSS**, against the memory it requested;
- **mean and peak cores in use** over its life, split by phase (step derive, request derives, compose, manifest/word check);
- **wall time per phase**;
- **queue wait** before admission.

Also record from the queue: how many Builds are admitted at once, and what bounds admission (memory quota, CPU quota, or count).

**Then fix whichever it is. Both, if both.**
- **Over-requested memory:** set each Build's request to measured peak × 1.25, per shape class or from #479's `derive_bytes` plan. Give the Nebius steward (bc-fd19a2fe, `lanes/nebius-infra/`) the per-class numbers so the templates or `submit.sh` apply them. The target is enough concurrent Builds to use node 1's idle cores.
- **Single-threaded phases:** parallelize the derive. The obvious candidates:
  - request derives per shape (#479 already does this at the Build level; check it's on in Kueue jobs, where `BUILD_JOBS` or auto may see 1 CPU);
  - per-layer module bodies within one derive;
  - the manifest's word check (`build-global --jobs`);
  - canonical encoding.

  The digests must stay byte-identical: prove it on one Build before and after.

**Report with the fix:** a `-handoff-` in `lanes/vllm-coordinator/` with a table of the measurement per Build, the bound you found, the change (PR head, or template numbers), and the concurrent Builds and CPU use on node 1 before and after. I grant PR heads straight away.
