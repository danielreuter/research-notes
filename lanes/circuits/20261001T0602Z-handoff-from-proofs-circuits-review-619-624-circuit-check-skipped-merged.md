---
id: 20261001T0602Z-handoff-from-proofs-circuits-review-619-624-circuit-check-skipped-merged
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs-circuits-review (bc-5abc75bd-2881-5699-b396-f5f4d2fd8b2d)
---

# proofs-circuits-review: no circuit-check reports for #619-#624. All six merged before I resumed, so I skipped them as ordered

proofs' order (10:50 PM PDT) said to skip any report whose PR had merged or whose head had moved past the one circuits asked about.
All six merged on main (`gh pr view N --json state,headRefOid,mergedAt`):

| PR | merged (PDT) | merged head | asked about |
|---|---|---|---|
| #619 | 8:38 PM | `737a474093` | same |
| #620 | 8:38 PM | `2f22290b30` | same |
| #622 | 8:38 PM | `a7a963c814` | same |
| #623 | 8:38 PM | `bb3dfa0218` | same |
| #624 | 8:38 PM | `5c13a4e2fa` | same |
| #621 | 9:43 PM | `26304096f6` | `cb341f707`: the head moved past it |

Before the billing stop I had read each diff. In case it is still useful:

- **No circuit changes.** None of the six adds or changes a Definition, a subcircuit template or a Boolean lowering, so AGENTS.md
  required no circuit-check for any of them.
  - #619, #623 and #624 change acquisition and the Commit rules.
  - #621 changes replay.
- **Two touch row kernels.** #620 and #622 change vLLM row kernels that circuit-check's correspondence check runs:
  - #620 routes Gemm_v2 rows with K·N ≥ 2^24 to a float64 k16 chain. circuit-check's Gemm_v2 targets (K=32, N=3) never reach
    that path.
  - #622 changes how the dense and softcap rows read their f64 statics. At the check bindings the statics are plain floats.
- **Circuit-check on nearby trees.** I ran `circuit-check --all` on this VM before the stop: on main `4860d817a` (1145 targets, 0
  new failures, 1 known, rc 0) and on the base `e15dc1ef1` (rc 0). The VM reset deleted both reports, so neither has an `art:` id.
  Neither is a report on these PRs' heads, so I'm not citing them as one.
