---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: open · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# Where the unit draw goes: in the clear, between registration and the session

**Question** (coordinator, relaying Daniel, 2026-09-27): the verifier now draws the sampled units from its own randomness.
Under batched, serialized sessions, where statements are fixed before the first coin, should the draw sit under the
session's up-front coin commitment, or be sent in the clear before the session starts?

**Answer: send it in the clear.** The order is: serving registers its roots, then the verifier draws and sends the unit
set, then the session's statements (the drawn units') are fixed, and only then does the verifier send its coin
commitment. The draw becomes part of the session's statement, and the session record keeps it. It should not go under the
coin commitment.

## What each property needs

- **Soundness** needs the draw to be uniform and independent of the prover's committed transcript. That transcript is
  fixed at registration (the desk study's `X(st)`). In the soundness game the verifier is honest, so fresh randomness
  drawn after registration suffices, and nothing needs committing. The audit bound also needs the first wrong sampled unit
  fixed before the session's first coin, so that the per-table theorem applies conditionally. A clear draw before the
  session gives exactly that.
- **Single-rewind zero knowledge** needs the session's statements fixed before the verifier's coin commitment, and every
  coin committed before the prover's first message. A clear draw is just part of the statement. The Goldreich–Kahan
  simulator receives it like any other verifier message and needs nothing more. A malicious verifier may choose any draw,
  even adaptively from the registered roots. That gains it nothing: the roots are statistically hiding Halevi–Micali
  commitments, and the draw only selects which true statements get zero-knowledge proofs. What leaks is the statements
  themselves, which is the same in either placement (ASSUMPTIONS.md §7).

## Why not under the coin commitment

- **It cannot stay hidden.** The prover must know the draw to know which units to prove. So it would have to be opened
  before the prover's first message, which is the clear draw plus a pointless commitment.
- **It breaks the model's invariant.** Statements would then depend on a committed coin, which breaks "statements fixed
  before the first coin". Both the per-table theorem's conditioning and the simulator's argument use that invariant as
  stated.
- **Binding buys nothing.** It only stops a verifier from changing its draw, and a malicious verifier may pick any draw
  anyway.

## Two notes

- **An early draw.** To save the round trip, the draw can be made before registration. It then has to stay hidden until
  registration closes: commit to it with a statistically hiding commitment (HM96 suffices) and open it right after
  registration. Only hiding matters there.
- **Exact samplers.** Use the exact samplers (`subset`, `bernoulli`) on the verifier's OS randomness directly, without
  `derive` or SHA-256 seeds. The sampling term then needs no hash assumption. The desk study flagged the PRF-type
  assumption that `derive` would otherwise need.
