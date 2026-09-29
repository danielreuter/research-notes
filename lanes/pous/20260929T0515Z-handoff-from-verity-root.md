---
id: 20260929T0515Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: argument traffic is an exfiltration channel the width rule doesn't bound

Desk BOTEC for Daniel, framed on exfiltration security (not PoUW window sizing): `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/argument-bandwidth-botec.md`. The figures are reproduced by `internal/argument-bandwidth-botec.py` in the same store.

- **Setup:** one 8×H100 node serves 70B FP8. Audits are sized so the served values leak at most 1% of the weights over the system's life at δ = 2⁻²⁰. That comes to about 0.82 drawn units per token.
- **Result:** the argument traffic sends about 3.1 Gb/s out of the node (one-stage public ZK). 7.4% of those bits are freely settable (24% with subverted ZK masks), enough to move the FP8 weights out in 40 min (13 min with the masks).
- **Bearing on the width rule:** the rule bounds wrong values in the served transcript. The free bits here are hiding randomness (hm96 salts on opened leaves, the free half of opened commit strings, ZK masks), and every check still passes when they carry ciphertext. Narrow-Z tightening doesn't touch this channel.
- **No draw rate fixes both channels:** a one-year leak time needs at most 0.35 settable bits per drawn unit, and today it's about 4,500.
- **Structural fixes (§7 ranks them):** a jointly trusted verifier box that outputs only the verdict and profile, or derandomized salts and masks.

No action is required from you. It's input for the open width-rule question and for any leaf-hash or ZK-mask design choices.
