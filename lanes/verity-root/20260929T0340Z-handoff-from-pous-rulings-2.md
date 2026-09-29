---
id: 20260929T0340Z-handoff-from-pous-rulings-2
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: more of Daniel's rulings (03:22Z), in reply to your 0338Z note

## Ruled

- **Work-proportional draw sizing: approved.** Tile draws are sized by work, with closure draws. Units that do no PoUW
  work (dequantization, the quantizer, attention) get an integrity floor of at least one draw each. This needs the new
  law version in `Flock/Draw.lean`, which is yours as draw-law owner; #167's sampler and one_stage's U2 check follow it.
  The closure-draw rule comes to you with §12's red-team verdict, as you asked.
- **Online verifier: accepted.** It is standard in our setting, and PoUW's credit is the verifier's own.
- **Leaf hash: stays conservative.** SHA-512 word leaves and a SHAKE256 noise XOF, with no switch to TurboSHAKE128;
  security comes before efficiency for now.
- **A-row retention:** the activations are regenerated on a batch-invariant serving path instead of being kept.
- **The Lean lag on `main`: allowed.** This comes from the lighter norms in our 0336Z note: the one match point is
  publishing or citing, `check` detects lag by itself, and branches are never constrained.

## Still with Daniel

- **The width rule.** There is a new recommendation: move the matmul result Z into narrow width-rule units, and allow
  wide units only where their outputs reach nothing observable. With a floor of about 220,000 narrow draws, that costs
  about 2% more proving and tightens the exfiltration bound 10×. It hasn't been red-teamed yet. We'll post the ruling
  here.
