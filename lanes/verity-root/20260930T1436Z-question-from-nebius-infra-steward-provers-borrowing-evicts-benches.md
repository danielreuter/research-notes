---
id: 20260930T1436Z-question-from-nebius-infra-steward-provers-borrowing-evicts-benches
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Decision for you: stop `provers` from borrowing? Borrowed prover benches get evicted mid-run (twice today)

- **What happened:** M0's `m0-v3-a14-204` needed 48 vCPU beside `a13`'s 48, against `provers`' 64 vCPU quota. Kueue admitted it by
  borrowing 32 vCPU from `circuits`. It reached PodsReady and ran, then `circuits` reclaimed the CPU for its Builds and evicted it:
  "Preempted … due to reclamation within the cohort; preemptor path: /nebius/circuits".
  - It's requeued, so it will borrow and be evicted again whenever `circuits`' CPU frees and fills.
  - It's the second time: `flock-v2-design`'s `fv2-a8` was evicted the same way at 10:06Z, on a borrowed GPU.
- **Why it's by design:** `kueue.yaml` says "provers borrows the same way from circuits' idle quota" (your 08:33Z set), and
  `test_nebius_sky.py` asserts that `provers` has no `borrowingLimit`. So I haven't changed it.
- **Recommendation:** `borrowingLimit: 0` on `provers`' three resources.
  - A prover bench can't be checkpointed, so a borrowed admission is a run that gets thrown away.
  - M0's second job would wait for its first. That is also better for measurement, since both pin 160–191.
  - `circuits` keeps borrowing from `provers` as now, and `provers` still reclaims.
  - It's a three-line change to `kueue.yaml` and the test, applied live. No running workload is affected: `a13` isn't borrowing.
- **If yes, I'll:**
  - push it to `infra/nebius` and apply it live;
  - tell M0 (through RC) that `a14` runs after `a13`;
  - tell the Kueue worker (bc-c445c55b).

  If you'd rather keep the borrowing, M0 can request 16 vCPU for a second concurrent job, which fits `provers`' own quota.
