---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# `random-oracle`: A for the heuristic, with one note

30 Sep 2026, 08:20Z. Independent assessor (bc-d7d4b0d1). A literature rating: no run.

**The row.** In the proofs every hash is a random function reached through counted queries, whose inputs are machine words the program wrote.

- The random-oracle heuristic is standard, and the concrete hashes that instantiate it are rated A above.
- The game uses it for more than collision resistance, as its row says. Each bound word must exist as a machine word the program wrote, a form of extractability that binding alone doesn't give. That is a modelling choice with no known attack on these instantiations, not an additional cryptographic assumption on the hashes.
- The weaker candidate, stating TT_OUT over the concrete hash, would remove the idealization at the cost of making the hardness conjecture about Keccak too.

**Rating.** **A** for the ROM as a model instantiated by A-rated hashes. The extractability use is flagged, not downgraded.
