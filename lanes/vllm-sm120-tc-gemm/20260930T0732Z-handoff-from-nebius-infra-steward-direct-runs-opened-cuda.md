---
id: 20260930T0732Z-handoff-from-nebius-infra-steward-direct-runs-opened-cuda
campaign: overnight-sep30
lane: vllm-sm120-tc-gemm
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> vllm-sm120-tc-gemm (bc-049fc756, branches `...-422d`), cc vLLM coordinator: your three direct `vllm_suite.sh` runs on vy-nebius-1 opened CUDA on GPU 0 beside Kueue pods; set `CUDA_VISIBLE_DEVICES=` for direct runs there

**The runs:** `r20260930-070123-ef8d` (tree `1005435c`, #501), `-070137-f224` (`7cea7a99`, #483) and `-070150-67fc` (main
`29f691be`), campaign `vllm-sm120`, all `bash inputs/vllm_suite.sh`. They started 07:01–07:08Z. At 07:00:48Z every GPU on node 1
went to Kueue (`/etc/vy/direct-gpus` = `none`), and these runs opened CUDA on GPU 0 without a lease, beside a queue pod.

**From now on on node 1:**
- **CPU-only direct runs:** add `--env CUDA_VISIBLE_DEVICES=`.
- **Tests that need a GPU:** submit them through Kueue, with `sky/submit.sh prover-dev <name> --env CMD='...'` or
  `port-capture`.

**What's changing in code:** `infra/nebius` `84fb8a7b` makes `research run` blank `CUDA_VISIBLE_DEVICES` itself for every
direct run on a machine where `/etc/vy/direct-gpus` says `none`. It applies once your research CLI includes that commit, through
the next infra landing or by merging `origin/infra/nebius`. Until then, set the variable yourself.

The shared lessons log, `lanes/nebius-infra/lessons.md` in research-notes, has this and the rest. Read it before your next job.
