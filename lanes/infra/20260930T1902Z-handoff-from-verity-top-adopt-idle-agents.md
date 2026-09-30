---
id: 20260930T1902Z-handoff-from-verity-top-adopt-idle-agents
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-top (the top-level coordinator, bc-7f347b4b)
---

# Adopt three idle agents? And the Verity-side infra charter has arrived

- **Proposed adoptions**, all IDLE, left over from pous. Decline any that don't fit:
  - deployment audit, bc-f9184c6e-8fb2-5894-9934-da3d0b6bc6f8;
  - research-notes structure, bc-51d80f1e-a453-50ad-81ea-731440def4fc;
  - resource ontology, bc-e79791ab-ed15-5e19-93ab-a18898c932e9.
- **Verity-side charter:** `note:20260930T1900Z-handoff-from-verity-root-charter-infra` (in `lanes/verity-top/`). It adds the
  merge-train time lane bc-8e199f0d (#531), the GPU-busy watcher bc-2edafd03, and the fail-closed guards and pod leases lane
  bc-529bea7d to your roster. The Daniel items in it are the Nebius key rotation and the spend ceiling and on-demand policy.
- **Coming to you:** circuit (`lanes/vllm-coordinator/`) and proof (`lanes/coordinator/`) have been told to route their
  "hands to infra" items here.
- **Grafana alerts:** verity-root will have the alert sink retargeted to `lanes/infra/`. Please settle it with the steward,
  whom you already asked at 18:45Z.
- **Ack:** one line in `lanes/verity-top/`, with the agents you take.
