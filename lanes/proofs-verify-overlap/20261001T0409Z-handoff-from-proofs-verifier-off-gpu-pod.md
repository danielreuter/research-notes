---
id: 20261001T0409Z-handoff-from-proofs-verifier-off-gpu-pod
campaign: verity
lane: proofs-verify-overlap
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Next after the overlap: run the verifier as a 0-GPU pod, so the GPU pod holds only the prover

to: proofs-verify-overlap (bc-96b9bb72). Proofs committed this to infra at 9:10 PM PDT (Slack thread 1790822262.591279,
infra's measurement in `internal/infra/node-1-gpu-idle-phases.md`).

- **Why:** from 1 PM to 7:32 PM PDT, proofs' node-1 pods held 14.3 GPU-h and were busy for 1.5. Tonight's node-2 gate
  (#1936, K=8192, 20 sessions) shows the cause: about 0.5 s per session on the GPU and 9 to 11 s per session in the
  verifier (`flock-circuit serve`) on the CPU, so the GPU waits on the verifier.
- **The task:** once the overlap works, run `serve` in its own pod with `gpu: 0` (in `provers`, or `deployments-cpu`), and
  have the prover's pod reach it over TCP instead of `127.0.0.1`. Then the GPU pod holds only the prover. Measure GPU busy
  against held on one K=2048 point, before and after.
- **Keep:** the session stays interactive (280 rounds, per-round handling in milliseconds), so measure the round-trip
  cost the pod network adds and report it beside the overhead.
- **Start:** on your restart after the billing stop. Your branch is at `42461143`.
