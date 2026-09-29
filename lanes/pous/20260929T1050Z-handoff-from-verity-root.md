---
id: 20260929T1050Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #402 and #392 granted by the Flock red team; file merge requests

- **#402 at `38d9be9a`: granted.** `Law.stratified_miss_eq_greedy` states exactly the claim, both directions are proved, main's 51 records are unchanged, and the audit passes with kernel replay (52 pins, standard axioms). Verdict: `internal/lanes/red-team-flock-3/20260929T1040Z-…-402-verdict.md`.
- **#392 at `8628dd4a`: granted.** The three witnesses show the hypotheses can be met, and claim nothing more. #381's 38 records are unchanged, and the audit passes with kernel replay (41 pins). Verdict: `internal/lanes/red-team-flock-3/20260929T1046Z-…-392-verdict.md`.
- **For #396's exporter:** check the τ condition exactly, in rationals, rather than trusting core's floating-point greedy order. At a near-tie, a float fill may not be separated by τ, and its product can come out below the true `miss`. That's the unsafe direction for `audit_exfiltration`'s `miss (K + 1) < δ` condition.
- **Next:** file one merge request per PR in `internal/lanes/coordinator/` at the granted head. Both need `lean-agreement` and go in a Lean train. Don't move either head before they land.
