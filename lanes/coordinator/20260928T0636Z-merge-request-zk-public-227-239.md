---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

# Merge request to the research coordinator (bc-8ece7cde): #227, then #239 (ZK Lean pins, granted)

From zk-public (the public-circuit ZK worker). Two soundness-package PRs whose pins the red team granted. Please run
`check` and `research merge` in order.

| PR | branch, head | adds | pins |
|---|---|---|---|
| [#227](https://github.com/danielreuter/verity/pull/227) | `cursor/zk-public-masking-lemmas-b710` at `e1947d5b`, on `main` `6746f408` (still `main`'s tip at 06:36Z; GitHub says mergeable) | `FlockSoundness/ZK/Masking.lean`, `ZK/Adaptivity.lean`, their imports, the soundness README's §3 line, 11 pins in `lean-audit.json` | 11 new, no existing pin changed |
| [#239](https://github.com/danielreuter/verity/pull/239) | `cursor/zk-public-coin-binding-b710` at `23d3d6fe`, stacked on #227 | `FlockSoundness/ZK/CoinBinding.lean`, its import, 1 pin | 1 new |

- **Statement reviewer:** the red team, bc-f0bc7e75 (lane red-team-flock-3). Its review `red-team-flock-3-zk-proof-public`
  (05:55Z) grants #227's eleven pins at `e1947d5b` and #239's pin at `92ce596e`. It rebuilt `Masking.lean` independently and
  checked each record against the source.
- **Since the grant:** #239's `23d3d6fe` changes docstrings only, rewording what the review flagged ("explicit collision"
  overstated the conclusion). `lean-audit.json` is unchanged; the audit compares clean.
- **What I ran:** `lake build` of the soundness package, and `tools/lean/audit.py backends/flock/verifier/lean/soundness`.
  PASS at both heads: 4,718 declarations and 20 pins with #227; 4,749 and 21 with #239. Axioms `propext`,
  `Classical.choice`, `Quot.sound`; kernel replay clean.
- **Not yet run:** the full `check` (pytest, `circuit-check --all`, every Lean package). Nothing outside
  `backends/flock/verifier/lean/soundness` changes, but `research merge` needs the recorded `check` of each exact head.
- **Order:** #227 first. #239 is stacked on it, so retarget #239 onto `main` once #227 lands. I'm marking both ready for
  review.
- **Not in this request:** [#245](https://github.com/danielreuter/verity/pull/245), stacked on #239, adds
  `coin_opening_binding_keyed` for the keyed coin tree. It awaits the red team's statement review.
