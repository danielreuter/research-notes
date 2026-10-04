---
id: 20261004T2110Z-finding-p2-direction-and-dead-ends
campaign: pous
lane: memory-accounting
kind: finding
status: open
repo: danielreuter/verity
origin: memory-accounting (bc-15ada664), the evidence for PoUS approaches registered 4 Oct whose sources were only in Slack or chat
---

# PoUS: Daniel's 4 Oct budget ruling, the dead ends it closes, and the P2 direction

## Daniel's ruling (4 Oct, in memory-accounting's chat)

- The cost-rule relaxations don't work for him. Those are certifying prefill only, certifying only batches of at least
  2,000, and partial coverage.
- He relaxes the 2× decode budget instead. The first goal is a scheme secure enough that nobody can break it.
- Nothing already done is thrown away: results, dead ends and the math are kept and organised (the migration).

## Figures behind the dead ends

These are old-accounting's figures, in `#agent-coordination` thread 1791138312.751569, message 1791139109.307919. Its
sources are the three P2/P3 documents relayed in `note:20261004T1836Z-report-relay-p2-verdict`,
`note:20261004T1836Z-report-relay-p2-spec-v1-frozen` and `note:20261004T1836Z-report-relay-p3-cryptanalysis`.

| Approach | Figure |
|---|---|
| Certify prefill only | P3 at 1.26–1.28× |
| Certify only batches ≥ 2,000 | P3 at 1.98× |
| Partial coverage | 2× only at φ ≤ 17.5% |
| Secrets erased at encode, public keyless decode | at most about 4.8% of \|C\| (27 Sep screen); the rest needs slow online re-expansion, a trapdoor or a sequential chain |
| Symmetric chains inside 2× | every label-graph layout reached at most 0.5% of the regeneration depth needed |

## The P2 direction (memory-accounting's recommendation; with Daniel)

The review is `art:f33b450f2cd48f6cec2057915ae08b2221a4a6060dc2f9fa38055e8e4d74b98c`, and the frozen spec is
`art:a7a29e84eef9d2584482b7f3e9722af6b579e2984a9633352564c562ce9e2021`.

- **Commit to P2 and spend the relaxed budget on margin.** Measure the cooperative root on CPU and GPU, then size w.
  - Rough scaling: root ∝ w^2.6 and decode per byte ∝ w^0.6.
  - About 40 kbit gives roughly 10× slower roots for about 1.7× decode.
  - The SeqRoot attack (`approach:pous/p2-seqroot-cooperating-cores`) is what this answers.
- **Red team** runs the hybrid bit/field solver against P2–M1-SGI (`approach:pous/p2-xor-reduce-compression`).
- **Name the excluded hardware** (VDF-style squarers) instead of leaving it implicit in the hardware class.
- **Fallback:** a symmetric wide final step, estimated at about 80–185× decode. It is secure without P2's algebraic
  assumption and is the scheme to build if P2 falls.
- The response window and w stay as frozen until Daniel rules on this.
