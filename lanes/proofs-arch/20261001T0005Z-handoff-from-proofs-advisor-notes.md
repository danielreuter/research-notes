---
id: 20261001T0005Z-handoff-from-proofs-advisor-notes
campaign: verity
lane: proofs-arch
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Uniform copies: the soundness package already models an instance as stacked copies of one net. Reuse it

The advisor (5:04 PM PDT): `Rows.stack` and `placement_stack` in the C-Flock soundness package
(`backends/flock/verifier/lean/soundness/`) model an instance as `upv` stacked copies of one net. Make the prototype's copy
model that one, not a new one, so its soundness story is already half-written.
