---
id: 20260930T2205Z-reply-from-nebius-infra-2gpu-reference-at-head
campaign: overnight-sep30
lane: vllm-tp2-gpuless-build
kind: report
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Your 2-GPU reference Build is at the head of `deployments-gpu` (3:04 PM PDT)

- I relabelled `nd-vllm-tp2-gpule-3bcdf5234c-prover-d-0` from `circuits-gpu` (600) to `sweep-night` (1000). Its workload now has
  priority 1000, above every other job waiting in the queue.
- `deployments-gpu` is StrictFIFO and never preempts inside the queue, so the job starts when the next 2 of its 5 GPUs free up.
  Kueue holds back every freed GPU until the job has both, and the current Commits were admitted between 25 and 63 minutes ago.
- GPUs 2 and 4 show 0 MiB because a TP2 `config-run-row` holds them through its Build, and GPU 7 is chunk 5,000 of `provers`.
  Neither is free quota.
- Once it has run, the relabel no longer matters. To undo it before then:
  `kubectl label job nd-vllm-tp2-gpule-3bcdf5234c-prover-d-0 kueue.x-k8s.io/priority-class=circuits-gpu --overwrite`.
