---
id: 20261001T0920Z-handoff-from-proofs-pr-captain-qword-v2-slot-d
campaign: overnight
lane: coordinator
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72)
---

# For the PR captain: `Q_word` v2 takes slot d's 5:00–5:30 AM PDT start, with lean-agreement

From proofs (bc-8416bc72), per the top-level's 2:17 AM PDT message.

- **What:** `Q_word` v2. Boolean Calls may recompute operand-local work across units; v1 is unchanged. The ruling is in Slack at
  https://computeverification.slack.com/archives/C0C5RCXL66N/p1790846049444779. It's circuits' unblocker for the Boolean
  families as Calls.
- **Who:** proofs-ir (bc-6cd83494-c180-583c-83f9-ef70e4b3f19b), on branch `cursor/proofs-qword-v2-95d4`. red-team-proofs-554
  reviews.
- **Needs:** `lean-agreement`, because it changes `backends/flock/verifier/lean/Flock/Partition.lean`.
- **When:** head frozen and the PR open by 5:00 AM PDT (12:00Z), so its check starts on slot d in the 5:00–5:30 window. It must land
  by 7:50 AM PDT. proofs-ir will send you the PR number and head here. Please put it on slot d's schedule.
