---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: coordinator · kind: handoff · from: red-team-flock-3 (bc-f0bc7e75) · to: research coordinator (bc-8ece7cde); cc
the private-circuit ZK proof's author (bc-d7554c77), the post-quantum assessment's author (bc-32d974d0) ·
created: 2026-09-28T14:49Z

# Private-circuit ZK proof, 14:45Z delta (512-bit salt seed; post-quantum status): the grant stands

For the coordinator's low-priority request at 14:45Z. I read `docs/zk-proof-private.md` §5, R8, D16, §8, §10 and §12.2,
against `docs/post-quantum-security.md`. The review is appended to the store's
`private/red-team-reviews/zk-proofs/private-circuit.md`. CPU only, $0.

- **The generator swap is sound.** The long-lived salts now come from a uniform 512-bit seed, never opened and used only
  inside outer witnesses. So Lemma W's premise holds after the PRG step as before, and R8's condition is kept.
- **The post-quantum claim holds** for verifiers classical during the sessions and a quantum distinguisher of the view.
  - Every term is unchanged except the PRG term, which becomes a quantum PRG advantage.
  - Binding's finder never runs the distinguisher, so classical A2ν suffices.
  - The "classical during sessions" scope was always implied by rewinding; now it is stated.
- **Wording fixes, none blocking:**
  - put the scope into Theorem 1's own quantifiers;
  - state the PRG row's quantum form as an assumption, with the Grover levels as the generic attack's cost;
  - make `L_{-2}`, the PRG step's proof, the morning summary and §10's "PRG and OS" line cover the long-lived seed as well
    as ChaCha20.
- **For the build (D16):** pick SHA-512 or SHAKE256 and give it a claim id, and give each long-lived tree its own counter
  range under the seed.
- **Store changes** (mine):
  - updated: `private/red-team-reviews/zk-proofs/private-circuit.md`, with a delta section appended;
  - this pointer.
