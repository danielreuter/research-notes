---
id: 20261001T0354Z-handoff-from-circuits-advisor-constraint
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: the advisor's hard constraint on fixes 1 and 2. Nothing that depends on the challenge moves before the root is fixed

From @old-circuits-and-proofs, circuits' research owner, 8:49 PM PDT (Slack 1790826524.716879). This is binding:
- **The replay sample is drawn from the run root** (`CH.root_seed` / `challenge_seed(run_root)`), and the slim bundle plans its reads
  from that draw. Neither the sampled-replay draw nor the slim plan may run in the pre-GPU `plan` task, or anywhere before the root is
  fixed. A prover who knows the picks before committing breaks soundness.
- **Fine in the 0-GPU plan task:** the acquisition (committer) plan and the warm-up plan, which don't depend on the challenge.
- **Fine in task 2 (sealing):**
  - the dumped store's blocks are verified against the already-fixed root (the bundle seal records that root, and the replay re-opens
    against it);
  - a device-retained store is copied to host before the GPU task exits.
- **One more gate row:** a golden row whose plan-task inputs are perturbed. The replay sample must not change.
- The plan doc is updated: `internal/circuits/commit-gpu-phases-plan.md`.
