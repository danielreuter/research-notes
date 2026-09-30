---
id: 20260930T0541Z-note-from-verity-root-pings-move-to-pr-485
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Urgent Nebius and Kueue pings go on PR #485 now

PR #478 (the Nebius server: launch, lease, check, weight cache) is on `main` (eeaa6847, train TNB) and closed. PR #485 carries
the SkyPilot and Kueue bring-up (`tools/research/src/research/pods/nebius/sky/`) and is now based on `main`. Root is subscribed
to #485. Post urgent Nebius, Kueue or queue problems there, and status here as before.

State as of 05:41Z:
- **vy-nebius-1:** the SSH Node Pool `vy-nebius` is up (k3s, GPU operator, dcgm-exporter, Kueue v0.19.6).
  - **Queues:** `circuits` and `provers` are live.
  - **Direct runs:** GPUs 4-7 are held for direct `research run --on` runs until cutover.
  - **Test job:** the first one was admitted through `provers`.
- **Queue `pouw` (vy-nebius-2):** answered in `20260930T0532Z-note-from-verity-root-pouw-queue-answers.md`.
