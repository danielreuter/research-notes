---
id: 20261001T0901Z-handoff-from-proofs-pr-captain-653-ready
campaign: overnight
lane: coordinator
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# For the PR captain: #653 (protocols layout step 1) is ready for a train before 7:50 AM PDT

to: the PR captain (bc-7ff3de9e).

- **The PR:** [#653](https://github.com/danielreuter/verity/pull/653), branch `cursor/protocols-merge-one-stage-95d4` at
  `f7c0bd246`. `protocols/one_stage` moves into `verity_sampled_proofs.one_stage`, one README replaces both `PROTOCOL.md`
  files, and Daniel's README ruling is in `friction/SKILL.md`. Daniel approved it at 12:05 AM PDT.
- **Its check:** `r20261001-074334-c292`, rc 0, SUCCESS, at tree `f7c0bd2462ec…`, lean-agreement included (it touches
  `backends/flock/`). It contained `origin/main` when checked.
- **Order:** it contains #642 (`34b483e78`) because soundness's audit inputs needed it, so train it after #642 or with
  it. It doesn't conflict with #638.
- **Priority:** below the Boolean IR, which the top-level put alone on slot b at 1:47 AM PDT. Any free slot after that is
  fine, as long as it lands by 7:50 AM PDT. If it can't, say so and I'll close it as a record, with the branch kept and the
  PR listed in `internal/proofs/backlog.md`.
