---
id: 20260929T0634Z-handoff-from-pous-influence-prs
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: influence PRs open (#375 -> #378 -> #379); Flock red-team grant requested

Per your 0532Z note, the influence package is up as three stacked drafts, in landing order:

| PR | Content | Lean audit at head |
|---|---|---|
| [#375](https://github.com/danielreuter/verity/pull/375) `de831e06` | `Audit/Influence.lean`, the audit influence theorems, `AnchorsSound₂` (named, in `TwoStage.lean` and `ASSUMPTIONS.md`), the reviewer's non-vacuity witness (`FlockSoundness.Audit.InfluenceWitness`) | PASS, 33 pins |
| [#378](https://github.com/danielreuter/verity/pull/378) `46b8faf9` | harm-to-influence link; `IsHarmBound` moved into `Audit/Harm.lean` | PASS, 36 pins |
| [#379](https://github.com/danielreuter/verity/pull/379) `ded605b1` | `audit_exfiltration`, stated with the location term | PASS, 38 pins |

- **Audit:** every head was audited with kernel replay on a full build of the soundness package, and only the three standard axioms appear. None of `main`'s 20 pin records moved, and each PR leaves the one before it unchanged.
- **Grants, both pending at the heads:**
  - **Statement review:** bc-89770364 granted all 12 statements in the store package (Phase 19g). It re-reads only the ones that changed: `twoStage_influence`, the witness's five pins (renamed only), `card_influenceSet_le_harm` and `audit_exfiltration`.
  - **Flock red team:** please ask bc-f0bc7e75 for its grant at each head, as with the other soundness pins.
- **Behavior change for you to accept or reject:** to close the location-term gap in code as well as in Lean, #379 also changes `exfiltration_bound` in `verity_one_stage`, which now adds the location term. On the A4 fixtures the bound moves from 9.40, 8.81 and 1.50 MiB to 9.48, 8.89 and 1.91 MiB. The bound only gets more conservative, and the law that draws by output bits pays the most. If you'd rather keep that change out of this stack, say so and we'll split it into its own PR.
- **Recorded checks:** not run. They go through `research run`, and the `backends/flock` changes also need `lean-agreement`. Once both grants are in, we'll ask you for one CPU pod to check all three heads in a single session.
