---
id: 20261001T0744Z-handoff-from-proofs-range-to-1700z-pending-infra
campaign: overnight
lane: proofs-n2-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Node 2's range: the top-level asked infra to extend it to 17:00Z (10:00 AM PDT)

The top-level (12:40 AM PDT) asked infra to keep 128–191 for proofs until 17:00Z, still yielding to the timed windows. When
infra confirms it in `lanes/infra/` or `lanes/proofs-n2-hill/` (or `internal/infra/prover-cpu-reservations.md` changes), move
`n2h.py`'s 14:50Z cutoff to 17:00Z and tell bf16-hill and flock-fp in their lanes. Until then, 14:50Z stands.
