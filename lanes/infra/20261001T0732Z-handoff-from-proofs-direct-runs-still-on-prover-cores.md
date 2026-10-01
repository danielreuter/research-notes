---
id: 20261001T0732Z-handoff-from-proofs-direct-runs-still-on-prover-cores
campaign: overnight
lane: infra
kind: handoff
status: answered
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Are direct runs from `main` kept off cores 128–191 now?

Daniel's 11:33 PM PDT ruling: infra keeps host processes and direct runs off proofs' prover cores 128–191 on node 1, so
`cpu-slice-shared` stops. proofs-flock-fp's clean re-runs were re-flagged three times by other lanes' work on those cores:
- **A `pouw` direct run and a `check`,** both launched from `main`. The pinning to cores 0–95 (`84fb8a7b`, `259acc56`) is only
  on `infra/nebius`, not on `main`.
- **Queued jobs.** `tools/cluster/descriptions/nebius.toml` reserves no `provers` range, so queued jobs get 96–191.

Details are in `note:20261001T0610Z-handoff-from-proofs-flock-fp-direct-runs-on-prover-slices` and the friction note
`note:proofs-flock-fp/20261001T0557Z-friction-direct-runs-unpinned-from-main`. Every re-flagged attempt carries a `note`
label naming its cause.

Is node 1 enforcing the ruling now, whatever branch a run is launched from? One line in `lanes/proofs/` is enough. If it
isn't, what's the ETA?

**Answered (infra, 07:30Z):** `note:20261001T0730Z-reply-from-infra-node1-prover-cores-enforced`.
