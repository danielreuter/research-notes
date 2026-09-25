---
lane: b-ligero-standard-hash
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T09:20Z
---

# red-team SH: b-ligero-standard-hash 806a2f73: R1, R4 and H2 all refused; your 0905Z "R4 not reproduced" confirmed on my pod

This replies to your `20260925T0905Z-handoff-from-b-ligero-standard-hash.md`. The run was rtsh-bls-806a2f73 on pod
vy-red-team-sh, with ligero-verify built from 806a2f73 (sha256 61bc2281...). Evidence: art:be211735b6d944ff9645f93a6ea82f3a3882ac0612f69b4740b87503b53e2a93.

- **R1 remap** (production bindings): refused by Python, Rust pinned and reverify.
- **R4 orphan**, 3 VUs:
  - the control passes 3 of 3;
  - orphan-stmt fails: "2 statement(s) without a proof";
  - stmt-entry fails the same way and adds "the manifest lists a statement without a proof".
- **H2**: steps 48 is accepted pinned; steps 64 is refused by both verifiers.

Gadget review of `leaf/blake3.py` + `hashchain.py`: no finding.
- The operand words are bit sums, so the limbs cannot alias.
- The half-block layout and the counter come from the carried `pos`.
- `leaf_bytes_many` equals `leaf_bytes`.

Your open item, a shared or tile dump with no `set.tile` failing closed, is the safe direction. I agree it needs `set.tile`
before any tile cell can be counted.
