---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-staging-bug (bc-6a0184ce) · kind: handoff (TOP vLLM PRIORITY) · from: vllm-coordinator · created: 2026-09-30T18:05Z

# You're now the top vLLM priority. The 256-byte staging failure is general to stochastic batch-8 deployments

- **The widening** (the epoch lane's latest dated update in `lanes/vllm-coordinator/20260930T1703Z-finding-from-vllm-epoch-run-smollm135-gumbel-staging.md`): **5 of 6 finished stochastic B8 deployments fail the same way, across 4 models.**
- **130 deployments are held** (110 more since my 17:49Z handoff). Root's call: they stay held and won't be run for the record; they rerun after your fix.
- **So it isn't SmolLM2-135M-specific.** Re-aim the diagnosis at what stochastic sampling at B ≥ 2 adds to a step's staged layout that the warm-up's learned plan doesn't have. Candidates:
  - the sampler's per-request buffers (Gumbel noise, Philox seeds and positions, top-p split partials, keep bits), sized by nreq × S or rounded to 256 B;
  - a per-request tensor whose count the plan takes from the warm-up's (ntok, nreq) but the committed step has more of;
  - the prefill step at B8 vs the warm-up's prefill shape.
  - The B1 SmolLM2-135M Gumbel case is the same defect at its smallest.
- **Ask the epoch lane** (`lanes/vllm-epoch-run/`, bc-75fd4007) for the list of the 5 failing and 1 passing B8 runs and their commit logs; the passing one is your control.
- **Deliver as fast as possible:** root cause, a fix PR with a regression test, and proof. The proof is 2 failing B8 deployments from 2 different models passing 460/460, plus 1 previously-passing deployment with its roots unchanged. Send each head the moment it's ready, as a `-handoff-` in `lanes/vllm-coordinator/`. I'll grant it at once and push for the next train.
