---
id: 20260929T0517Z-handoff-from-pous-lean-tiers
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Daniel's three Lean tiers, folded in, with every protocol placed

**Ruling (Daniel, 05:04Z):** an implemented protocol is in one of three tiers:

1. no Lean proof;
2. a Lean proof with no mechanical connection to the code;
3. a Lean proof mechanically connected to the code that runs.

Tier 1 is fine in exploratory code as long as it helps research velocity, tier 2 is fine for many applications, and
tier 3 is the target. This replaces question 2 of the Lean-first assessment (must pins be stated about the executable
spec?), which is now marked decided.

## Where it's written up

In the POUS store, edited in place:

- `docs/lean-first-protocols.md`, sections "Tiers", "Where each protocol stands" and "Where the tier rule lives";
- `docs/process-design-for-research-velocity.md` §5b, which reads the tiers through the `process-design` skill's tests
  (#359).

## What we decided or propose

- **Tier 3 means:** the verifier's trusted code (its decision, draws and setup) runs as compiled Lean; a pinned headline
  theorem's `reads` covers those modules; and every escape has vectors. The prover needs no connection, because
  soundness holds against every prover.
- **Vectors alone stay at tier 2.** They stop at toy sizes (band labels at `d = 1`, deployed at `d = 12`), `check`
  regenerates none of them, and divergences have sat beside passing vectors: P2's ChaCha8 keys, P3's `H`, the dense tag.
- **Provisional tier-1 norm:** tier 1 is fine for exploratory schemes whose results carry the tier as a label and are
  never cited as proved.
  - They move to tier 2 at the one match point (published or cited as secure), or once their certificate names a
    theorem.
  - They move to tier 3 when someone else relies on the verifier's decision, after a proof/code divergence, or when
    it's one theorem away.
- **Placements on `main`:**
  - Tier 1: the POUS band, P2 and P3 (for the implemented `H`), PoUW `ncp-v1`, H-1T, the two-stage law and the network
    warden. The band, PoUW and H-1T have tier-2 proofs in the store.
  - Tier 2: POUS dense (random-oracle `H`) and the one-stage audit.
  - The Flock verifier is tier 2 overall and tier 3 for its typing, layout and derivation checks.
  - Pearl's scheme is exempt.
- **Finding:** every POUS certificate names a theorem that no `lean-audit.json` on `main` pins (`band_meets_64`,
  `chain_meets_64`, `P2MeetsM1pB19Uncond`), yet the storage profile cites it.
- **Home, proposed and not built:** a tier field computed from the certificates and `lean-audit.json`, which `check`
  prints and the site shows. It needs no `AGENTS.md` line and no skill change; build it with the docs exporter.

## Open for root

- Should an off-`main` proof count toward `main`'s tier? We recommend not.
- Should a certificate naming an unaudited theorem fail `check`? We recommend labelling it rather than blocking.
- Should the one-stage audit be the tier-3 pilot? It's one theorem away: `Flock.Draw.derive` samples the model's law.
