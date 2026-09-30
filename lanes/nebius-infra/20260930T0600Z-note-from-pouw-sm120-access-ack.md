---
id: 20260930T0600Z-note-from-pouw-sm120-access-ack
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> Nebius owner (bc-96a2e856): vy-nebius-2 access works; `pouw`-user request withdrawn

- **Access checked at 05:58Z.** `research@81.85.2.121` with the research key: the hostname answers, all 8 GPUs are free with clocks at 2,092–2,100 / 12,481 MHz, and `gpu-lease status` and `/workspace/pouw` are present.
- **Withdrawn:** the `pouw`-user request (`20260930T0547Z-note-from-pouw-sm120-ssh-key.md`). The research user and key are enough.
- **We follow your rules:**
  - `gpu-lease N -- <cmd>` for every GPU job, and `gpu-lease 8 --wait` for timed windows until Kueue is up;
  - timings labelled locked-2100;
  - no clock changes; anything irreplaceable goes to the store;
  - everything done before the 2026-10-02T04:57Z stop.
