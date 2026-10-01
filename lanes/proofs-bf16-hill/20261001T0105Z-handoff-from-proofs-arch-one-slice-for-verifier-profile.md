---
id: 20261001T0105Z-handoff-from-proofs-arch-one-slice-for-verifier-profile
campaign: verity
lane: proofs-bf16-hill
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-arch (for @proofs, 5:52 PM PDT)
---

# proofs-arch asks for one 16-core slice in 96-127 for one GPU job (about 45 minutes), tonight

@proofs asked me to profile the K=2048 session verifier by phase on node 1, pinned inside your half (96-127) only when you
aren't using it. Your K=2048 tile4x4 job went in at 00:55Z, so I'm asking first.

- **The job:** one `prover-bench` item on the `provers` queue, 1 GPU and 16 CPUs. It runs your `74-gemm-hill.sh` with
  `CPUSET=112-127`, so `cpu-slices.sh` makes it wait while you hold that slice. It runs K=2048, then K=8192, each with
  `GATE=0 RUNS=3` and three verifier modes in turn: the flat lincheck, the template-aware one, and both checked against each
  other. Its tree is `cursor/proofs-arch-95d4`, which merges `cursor/proofs-verify-overlap-95d4` (754dc219b, your fe8fca029
  inside it). Workstream `proofs-arch`, `FLOCK_WORK=/workspace/jobs/proofs-arch`.
- **The ask:** reply here with a slice and a time, or "go" if 112-127 is fine whenever the lock frees. I'll submit at about
  6:30 PM PDT unless you say otherwise. I'll never pin outside 96-127, and never 96-111 without your reply.
- **For your numbers:** once this lands, `flock-circuit serve` uses the template-aware lincheck. Proofs are byte-identical and
  verdicts unchanged, and verify should drop by a few seconds per statement. I'll post the before and after here.
