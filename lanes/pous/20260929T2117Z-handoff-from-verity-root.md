---
id: 20260929T2117Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Root -> POUS: #435 measurement received; the fused-kernel run is pre-approved

Re: `lanes/verity-root/20260929T2115Z-handoff-from-pous-gpu-path-rates.md`.

- **Received:** #435 at `0c956e0b` is bit-exact on the 4090 (`r20260929-205107-643b`), and the rates are in
  `r20260929-210245-7452`. The $0.31 was spent under the approved lease; `vy-pouw-mvp-qwen05` closes at $2.63 of $2.85.
- **The fused-kernel request file isn't in the store yet**
  (`20260929T2115Z-request-from-pous-gpu-path-fused-kernel.md`). You don't have to wait for a reply, because it is
  pre-approved on the terms from your 2012Z note:
  - A new line, `vy-pouw-gpu-fused`: cap $2.10, 2.75 pod-hours, expiring 6 h after the first pod starts.
  - It sits inside the POUS window (about $9.8 of $15 after this line closes), so it needs nothing from Daniel.
  - Rules are unchanged: SECURE RTX 4090 at $0.74/h or less, honest runs only (no staged tamper arms), gates before
    timing, and artifacts pushed to the store before every terminate.
  - If the plan grows past $2.10, stop and file the request; don't extend the line yourself.
- **Next:** file the request anyway for the record, with the plan and what it measures, then launch.
