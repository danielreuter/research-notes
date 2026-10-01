---
id: 20261001T0730Z-handoff-from-proofs-750-is-a-deadline-not-a-stop-proofs-n2-hill
campaign: overnight
lane: proofs-n2-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# 7:50 AM PDT is a deadline, not a stop; 14:50Z stays until I say the range is extended

Daniel, 12:22 AM PDT: nobody stops before he wakes (about 9:20 AM PDT), and GPUs and cores stay full.

- **The range:** infra's note `note:20261001T0703Z-note-from-infra-node2-prover-cores-live` gives 128–191 through `vy-provers`
  until 14:50Z. I've asked the top-level to extend it past 7:50 AM PDT. Keep `n2h.py`'s 14:50Z cutoff until I write here that
  it's extended, and then move it to the new end.
- **After parity:** tell bf16-hill and flock-fp in their lanes, as planned (both know to wait for your word).
- **0-GPU items:** proofs-arch may put `gpus: 0` items in `ready-n2/proofs-arch/` (its old-fold half, about 20 min of one
  slot). Take them only when a slot is free and no GPU point is waiting.
- node2-ops released the 11 old `pn2g-*` jobs at 06:49Z; they withdrew themselves (no `PN2G_QUESTION`), so nothing is left
  of them (`note:20261001T0705Z-handoff-from-node2-ops-pn2g-released-withdrew`).
- **Anything that needs Daniel:** write it in `lanes/proofs/` as `needs-daniel:` with your recommendation, and carry on.
