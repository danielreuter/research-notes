---
id: 20261001T1603Z-handoff-from-proofs-554-successor-root-merges
campaign: proofs-hillclimb
lane: proofs-arch
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# #554's successor: root merges it on a passing check

to: proofs-arch. Root ruled yes at 8:45 AM PDT (`note:proofs/20261001T1545Z-handoff-from-verity-root-c-flock-prover-and-554-yes`),
and the research owner agreed (Slack `1790869365.170629`). Root merges the PR with `research merge` by 11:30 AM PDT.

- Open the PR with its head frozen. Push nothing to the branch after you record `check`.
- Record `check` on a pod with lean-agreement: `uv run python tools/check/check.py --record --on POD`.
- When it passes, write the head SHA and the check run's id in `lanes/proofs/`, and I send them to root.
- If `check` fails, write me the failing suite and your fix plan. Don't move the head without saying so.
