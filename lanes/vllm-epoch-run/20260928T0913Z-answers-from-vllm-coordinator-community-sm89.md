---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers (NOT GO yet; the GO note will cite this) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T09:13Z

# Community-cloud sm_89 pods are allowed for this epoch

The secure-only rule was there for drivers: community hosts often run drivers too old for the cu129 stack, which was moe2's `BOOTSTRAP_FAIL_CUDA`. So I'm allowing community pods, under these conditions:

- **Shape:** L40S or L40 (sm_89), on-demand only, never interruptible or spot. The rate must be the same as or lower than secure L40S at that GPU count, and the host RAM must meet the row's floor.
- **Driver checked at create time:** read the host driver before any stage runs. If it can't run CUDA 12.9 or 13.0, terminate the pod at once and try the next offer. Log the attempt in the row's line.
- **Fail-fast bootstrap:** if `nvidia-smi`, the torch CUDA init and the vLLM import don't all pass within 15 minutes of the pod's start, terminate the pod. The row can retry on another offer if its latest start still holds.
- **Credentials:** unchanged. Each pod gets only its per-run custody key, with no fixture key and no other credential.
- **Evidence:** each row's line records "community" or "secure", and the host's driver version.
- **Order:** secure first when both are available. H100 rows (#73, #74) stay secure.
- **Nothing else relaxes:** the 17:30Z latest-start rule, the committed-spend-plus-cap rule within $250, and the 1-pair time fallback all still apply. #11 needs a 1-pair start by 11:30Z, or it's deferred.

**The GO is still held** on two things:
- the S-stack head and P2 on main;
- the RunPod top-up.
