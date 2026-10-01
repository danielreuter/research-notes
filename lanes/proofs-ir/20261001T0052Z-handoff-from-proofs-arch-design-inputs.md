---
id: 20261001T0052Z-handoff-from-proofs-arch-design-inputs
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Design inputs from proofs-arch's restructure study, for the Boolean IR note

Read `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/internal/proofs/flock-restructure-study.md` (prototypes in
`backends/flock/arch_proto/` on `cursor/proofs-arch-95d4` @ `94993e0f9`). Three of its levers depend on what the IR can
express, so the design note should say where each one fits:

- **Step-sized slots (uniform copies).** Committed bits per MAC fall from 2,048 to 1,170 at K=2048 and from 4,096 to
  2,048 at K=8192. Prover overhead falls from 4.97e6 to 3.0e6 and from 9.84e6 to 5.0e6. This needs the IR, or whatever
  the prover reads, to expose template instances as uniform copies (slots), so the prover can commit one slot per step.
  Soundness is covered by `placement_stack`. Daniel's order is uniform copies first.
- **Hashing each row once per statement.** This brings both K to about 540 bits per MAC and prover overhead to 1.7e6. It
  needs cross-block wiring that today's block statement can't express. The format is a decision for Daniel; give it your
  recommendation.
- **Lookups.** They add 18% on top, and each one must replace about 45 committed bits to pay off. This is the likely
  fourth primitive kind (`Table`).
