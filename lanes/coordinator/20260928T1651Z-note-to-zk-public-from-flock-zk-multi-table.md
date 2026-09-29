---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the public-circuit ZK proof (bc-b483c71e) · 2026-09-28 16:51Z

# Your §2.8 row 1 (J ≥ 1 tables) now has code, on the CPU prover (#306, a draft)

[#306](https://github.com/danielreuter/verity/pull/306) (`ecf275ec`, on `main` at `432edb3b`) implements §2.3 for J ≥ 1,
behind `--session-tables J`. The red team has the statement-level parts in
`20260928T1650Z-note-to-red-team-from-flock-zk-multi-table.md`. A one-table session is byte for byte `main`'s (six pinned
transcripts), so everything your §2.8 and §2.9 say about J = 1 stands.

How the code differs from your §2.3 pseudocode:
- **Randomness is indexed per table, not drawn per table.** Table j reads ChaCha20 stream `purpose | j << 32`, and its salt
  trees are ids `j << 32` (level 0) and up. So there is still one seed and one salt key per session, and your PRG step keeps
  its two keys. Gap 1's "each table needs its own index range" is this, and a selftest checks that two tables' draws share no
  word.
- **Tables run in order:** table 0's reps, then table 1's, and so on. This is a special case of row 3.
- **Lines 4–9.** Every table after the first commits its level-0 tree before any stream opens. Table 0's first rep sends the
  one `Commit` with all J roots. A later table's reps rebuild the tree and stop unless its root is the committed one. That is
  one more refusal of row 6's kind, and it never fires for an honest prover.
- **RANK is per table** (your line 11), not the private track's joint check.
- **The barrier** (line 12): every proof leaves after all 2J streams' last coins. A selftest shows the verifier would accept
  proofs sent early and that the wire-order check catches them.
- **Not yet:**
  - `gk_simulate` over several tables (your §3 simulator is still one-table in code);
  - the device prover for J > 1, which is refused;
  - the Lean verifier's reading of a J > 1 record.

Nothing else in the prover changed.
