---
lane: coordinator
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T13:35Z
---

# L40S route (a) cells for #101 registered (art:e1a2dfc3, art:7a0d186b); merge request for cursor/agkr-l40s-101-f806 (bundle)

Your 11:44Z goal is done at about $3.5 of the $6. All four pods are terminated: the US-TX-4 pair at about 13:03Z and the US-NC-1
pair at 13:31Z. Every attempt is preserved.

| cell | art | plateau | VU/s | overhead (L40S line) | pods |
|---|---|---|---:|---:|---|
| K = 2048 on art:123dc234 | art:e1a2dfc3 | 2,048 VUs (4,096: OOM) | 326 | 2.7e8× | US-NC-1: L40S prover, H200 verifier (the DC's only stock) |
| K = 8192 on art:927a4c3a | art:7a0d186b | 512 VUs (1,024: OOM) | 74.7 | 3.0e8× | US-TX-4: two L40S pods on different machines |

- Both cells were planned through PR #74's placement check and passed `bench.cell check`. Both render on the L40S line with only
  the "not independently verified" code. Handoffs: `lanes/verify-flock-pure/` and `lanes/red-team-flock/`
  `20260926T1335Z-handoff-from-agkr-real-k.md`.
- **Merge request:** branch `cursor/agkr-l40s-101-f806`. GitHub refuses the token for push, so the branch is only in
  `lanes/agkr-real-k/evidence/agkr-l40s-101-f806-508e6e74.bundle`, on top of main 961d0667 (`git fetch <bundle> HEAD`). It
  contains:
  - 369d741c: `cell.sh` threads from the cgroup quota (v1 too).
  - c1e7bded: the merge of main.
  - 1a1bb6a2 and 47dcd5a4: the open-connection RTT probe on an echo the verifier serves; the probe waits for it.
  - 508e6e74: `bench.cell register` waits up to 600 s for the prover run's run files and refuses without them. This one touches
    the shared harness.

  Tests: `backends/numerical/tests/bench` 510 passed; `backends/gkr/tests/test_real_k.py` 8 passed. Draft PR #78
  (https://github.com/danielreuter/verity/pull/78) is open, but GitHub has the branch only at 369d741c. Pushing the bundle's
  head to `cursor/agkr-l40s-101-f806` updates the PR, or reopen me once the token works.
- **Why 508e6e74:** my first K = 8192 registration (art:4f7b26a5, 13:02Z) ran before the pod had published its attempt, so it
  had no run files and the views reject it. It's labeled `superseded_by` art:7a0d186b.
- **Not registered:** the first L40S K = 2048 run (r20260926-123236-c272) timed TCP connects (1.08 ms over global networking)
  instead of rounds (about 0.14 ms), and `bench.cell` refused its interaction check. The open-connection probe fixed that.
- **Stock at 13:07–13:10Z:** US-NC-1 had one L40S (now my terminated prover) and an H200, with no other GPUs and no CPU pods.
  US-TX-4 had L40S only.
- **Still open, for you:** art:a0ca8ef6 and art:a979dfcb (the A100 re-sweeps) have no verification label yet. Once they do,
  please write `superseded_by` on art:95fdd0ae (→ art:a0ca8ef6) and art:20197f8b (→ art:a979dfcb). I'm writing FINAL, so I
  won't be there to do it:

  ~~~text
  research data label art:95fdd0ae8974d305b7e6d2c8030082b0661c14f390489f91553e90d149e4ada7 superseded_by \
    art:a0ca8ef6d126f9cc1b4e7cc440b802d8030407d6f26e8c8187a4bc5a2626075d --by agkr-real-k --ref r20260926-095028-c0bd
  research data label art:20197f8badd7bc43e61654f41f4f63144df8e4f5c21dbe781860fea59dd6917a superseded_by \
    art:a979dfcbd8014d8620320e228b66aba6d054f572c6e0fc3831b55de3cd94e32c --by agkr-real-k --ref r20260926-101301-8697
  ~~~
