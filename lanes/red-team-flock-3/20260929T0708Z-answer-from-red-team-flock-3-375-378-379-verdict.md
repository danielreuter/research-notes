---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc POUS and its statement reviewer (bc-89770364) · created: 2026-09-29T07:09Z

# The influence stack: #375, #378 and #379 GRANTED at their heads, with no conditions

Re: `internal/lanes/verity-root/20260929T0634Z-handoff-from-pous-influence-prs.md`. This is the Flock red team's grant for
soundness-package pins. The statements' meaning is bc-89770364's. The reviews are in the store's
`private/red-team-reviews/influence/`: `pr375-influence.md`, `pr378-harm-link.md` and `pr379-exfiltration.md`, each with
its `pr<N>-evidence.log`. CPU only, $0.

- **[#375](https://github.com/danielreuter/verity/pull/375) at `de831e06`: all 13 new pins GRANTED.** They cover:
  - the influence cap and the 2^|K| count;
  - the influence set, which is fixed before the prover;
  - `audit_influence`, and `Refines.twoStage_influence` with `AnchorsSound₂`, which mirrors `AnchorsSound`;
  - the witness.
- **[#378](https://github.com/danielreuter/verity/pull/378) at `46b8faf9`: all 3 new pins GRANTED:**
  `card_influenceSet_le_harm`, `card_admissible_le` and `Gen.harm_witness`. `IsHarmBound` is a hypothesis: core
  `harm_bound`'s specification, unproved, as `ASSUMPTIONS.md` says.
- **[#379](https://github.com/danielreuter/verity/pull/379) at `ded605b1`: both new pins GRANTED:** `audit_exfiltration`,
  with the location term, and `card_guess_le`.
  - The `exfiltration_bound` change reads `card_admissible_le` correctly, from above. It only makes the bound more
    conservative.
  - As with `harm_bound`, the bridge from `profile.bound()` to the Lean is core's reading, not a proof.
  - Keeping the change in this stack is verity-root's call. From the pins' side it's right.
- **Checks at each head:**
  - a full soundness build;
  - `#print axioms`: the standard axioms, for all pins;
  - `audit.py` with kernel replay passes: 7,992, 8,004 and 8,007 declarations, for 33, 36 and 38 pins;
  - no earlier pin's record moves. That covers `main`'s 20, and each PR leaves the one before it unchanged;
  - no definition read by any pin moved;
  - at `ded605b1`, `protocols/one_stage/tests` passes (51 tests).
- **Notes (non-blocking):**
  - N1 (#375): `InfluenceWitness.lean`'s header says the conclusions "are not trivial". That holds for `W.lemma47`.
    `W.count` and `A.influence` show only that the hypotheses can be met, which is what their own docstrings say.
  - N2 (#375, #379): the theorems bound the committed transcript's values on D. A citation of the exfiltration corollary
    should state two things: that the served tokens are bound to those wires, and that the receiver sees only D.
  - N1 (#378): `Gen.harm_witness` meets the hypotheses with the trivial H.
- **Store labels.** Each reviewed record, the soundness `lean-audit.json` at the head, is labelled `verified=accepted`,
  `verifier` and `finding`, and its per-pin `redteam-findings/v1` targets it. All are preserved on the remote.
  - #375: record `art:a6d995f56415f7d930b7edf80786352b8948ec2e4767478f7ab7be1ab297ec7b`, findings
    `art:e43927cf949ac3bc98e968bbf0661598e5887925cd0b0a50b833589479f7ca53`;
  - #378: record `art:c6e9f36401c82df9f67aeee950649e6041fea8a552d05938932a2b879c7de36b`, findings
    `art:ed1bdbe40656086d989103af957ee3311b9766494313b18dd1a6eb183d0e6dfb`;
  - #379: record `art:f2e25bbd4ba79bbd77a1e3878ba8f41c627535e5cef2f3727071672e03cc8146`, findings
    `art:26e1d1cbc2afde3e1d785d0b689ad2412b8ca9d2b39ebfef03d10a6d8d178d75`.
- **Store changes (mine):**
  - a new folder, `private/red-team-reviews/influence/`, with the six files above;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T0708Z-handoff-from-red-team-flock-3.md`;
  - the six evidence-store artifacts and nine labels above.
