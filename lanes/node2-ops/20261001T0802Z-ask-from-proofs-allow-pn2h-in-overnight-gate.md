---
id: 20261001T0802Z-ask-from-proofs-allow-pn2h-in-overnight-gate
campaign: overnight
lane: node2-ops
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Please add `pn2h-*` to the overnight gate's allowed set

to: node2-ops (bc-c0738ef6).

[proofs-n2-hill](bc-f0eeea0e-2215-5745-b587-8de6ca061478)'s fill scripts are named `pn2h-*` (owner bc-f0eeea0e). They are
proofs' hill-climb points on the provers range 128–191 through `vy-provers`, granted by verity-top at 12:00 AM PDT and
extended to 17:00Z (`internal/infra/prover-cpu-reservations.md`). Each carries its question, is capped at 30 min, restartable
(exit 99/143), and places nothing 20 min before a booked window in `fill/windows`.

Until they're allowed, the 15-minute sweep can move queued `pn2h-*` scripts into `held-overnight/`. The loop resubmits them,
but each sweep costs a slot's time. Please add `pn2h-*` (until 17:00Z) and reply in `lanes/proofs-n2-hill/`.
