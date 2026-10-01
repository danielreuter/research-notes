---
id: 20261001T0708Z-handoff-from-proofs-daniel-yes-session-preflight
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Daniel said yes to one preflight check per GPU session

Daniel, 12:05 AM PDT: the preflight check runs once per GPU session, one per distinct K, never shared across K. Each job cites
its session's preflight `art:` id and refuses to count itself if its key differs. That is your design with my defaults.

I asked the research owner for its yes on the confirming run at 12:07 AM PDT (Slack thread `1790833483.081999`). Still don't
submit: build, push and write the spec to `lanes/proofs/`, then reply; I'll resume you with the research owner's answer.
