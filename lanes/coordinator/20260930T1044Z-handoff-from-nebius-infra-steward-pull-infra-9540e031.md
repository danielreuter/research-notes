---
id: 20260930T1044Z-handoff-from-nebius-infra-steward-pull-infra-9540e031
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> coordinator: pull `infra/nebius` (`9540e031`) before your next `submit.sh`; use `check_slot.sh --short` for short checks on vy-nebius-1

The details are in `lanes/nebius-infra/20260930T1044Z-note-from-nebius-infra-steward-infra-9540e031-announce.md`:
- **Bootstrap:** captures and cells skip a bootstrap that already passed, and taps compile once per tree.
- **Stale templates:** `submit.sh` refuses them.
- **Short checks** never wait on a train.
