---
lane: red-team-flock
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T13:35Z
---

# Review request: A-GKR route (a) on an L40S prover for #101, art:e1a2dfc3 (K = 2048) and art:7a0d186b (K = 8192)

This is a new line for A-GKR: the L40S, which the workload headline counts. The statements, pins, verifier and gate code are the
same as in the A100 real-K cells you have (art:a0ca8ef6, art:a979dfcb). What's new is the prover's GPU, the placement, and how the
RTT is measured. The L40S line needs its own verdict.

| cell | plateau, VU/s | prover (pod, machine, public IP) | verifier | DC, link |
|---|---|---|---|---|
| art:e1a2dfc3 K = 2048 | 2,048, 326 | L40S bdm1su2c4x7my1, av7yp9ygnbzg, 103.196.86.5 | H200 qz4cc7wzj5nke2, hl5m5gd6160a, 103.196.86.193 | US-NC-1, global networking 10.0.224.208 |
| art:7a0d186b K = 8192 | 512, 74.7 | L40S oa0m0tx3c6vxrm, h1ovgmmrd3dh, 195.26.232.178 | L40S nqkz63dauxz4ql, bmf6gxxmufbv, 195.26.232.152 | US-TX-4, global networking 10.0.129.112 |

- **Placement:**
  - Both cells were planned through PR #74's `bench.cell plan`, which reads the pods' RunPod machine ids and public IPs, and they
    passed `check`, where each run's `placement.json` boot ids differ. The machine ids also differ in the RunPod API.
  - The US-NC-1 verifier is an H200 because that was the DC's only stock at 13:10Z (no L40S, other GPU or CPU pods). A different
    GPU type can't share a host with the L40S.
  - Machine av7yp9ygnbzg also hosts another lane's L40S pod, `vy-flock-ir-lowering-a-l40s` (cwctydjt1cf25a), on another GPU of
    that host. It could be a contention source on the prover's side. It doesn't affect the placement, and the timing guard saw no
    other GPU process in our container and a host load of at most 18.6 of 128.
- **RTT method:**
  - The prover times 50 ping-pongs of 8 bytes on one open TCP connection to an echo on the verifier pod (port 7201,
    `cell.sh`). The probe gave 0.131 ms (K = 2048) and 0.214 ms (K = 8192); the in-session RTTs were 0.220 ms and 0.349 ms.
  - The first L40S K = 2048 run (r20260926-123236-c272) timed TCP connects instead. Over RunPod's global network a connect costs
    about 1.08 ms, against about 0.14 ms per round inside a session. With route (a)'s ~3,950 rounds, the interaction model came
    out 31% slower than measured, and `bench.cell` refused it. That run is not registered, and its auto-published results are
    rejected in the views.
- **Gate:** on the L40S at K = 2048, r20260926-123236-c272's gate passed. The honest prover was admitted except for non_producer;
  a stale prime state was rejected by R2-prime; the FS prover and the wrong-K claim were refused. The two registered runs
  skipped the gate (GATE=0).
- **Contention:** the timing guard recorded CPU throttling in 19% and 16% of the cgroup's periods (quota 13.6 cores). Per the
  recorded rule, that isn't applied: route (a)'s Flock prover uses the pod's whole quota by design.
- **Shared harness change:** in 508e6e74, `bench.cell register` waits up to 600 s for the prover run's run files and refuses
  without them. My K = 8192 registration at 13:02Z had none, because the pod hadn't yet published its attempt. It is replaced
  by art:7a0d186b, and art:4f7b26a5 is labeled `superseded_by`.
- **Code:** `lanes/agkr-real-k/evidence/agkr-l40s-101-f806-508e6e74.bundle` (branch `cursor/agkr-l40s-101-f806` on top of main
  961d0667). It isn't on GitHub because the token is refused.
