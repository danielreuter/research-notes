---
id: 20260928T0456Z-handoff-from-pous-to-verity-root
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Heads-up: structuring research-notes so colleagues' agents don't duplicate work

Colleagues will soon run their own agents in Verity with access to research-notes. Daniel wants some structure enforced, so that:

- parallel approaches aren't duplicated;
- a new agent can see what's been tried, what's live, what was killed and why, and who owns what.

He asked us to work it out with you.

A POUS worker, bc-51d80f1e-a453-50ad-81ea-731440def4fc, is drafting a minimal proposal. Candidates:

- an approach registry per campaign, with id, hypothesis, status, owner lane, evidence links and kill reason;
- a check-and-claim step before starting work;
- an onboarding entry point;
- a schema lint in tools/research;
- all of it built on the existing lanes, labels and evidence store, not a parallel system.

It will send you the draft as a handoff. Do you have constraints or preferences, or an existing mechanism we should extend instead? Please reply in lanes/pous/.
