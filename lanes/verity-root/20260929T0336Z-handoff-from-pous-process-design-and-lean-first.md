---
id: 20260929T0336Z-handoff-from-pous-process-design-and-lean-first
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Daniel's process-design skill and the Lean-first norms (sync; please relay to the research coordinator)

Daniel asked us to sync these with you and the research coordinator.

## Decisions Daniel has made (29 Sep, about 03:05–03:35Z)

- **Lean-first protocols:** the Lean is the spec. The Python only has to match the vectors the Lean generates, and it
  doesn't call compiled Lean. The Flock verifier is unchanged.
- **Lighter syncing norms:** the Python must match the Lean at one point only, when a result is published or cited as
  the protocol's. `check` detects lag by itself: the Python may fail a vector case only if that case's expected value
  changed since the Python last passed it. There is no hand-kept lag list, and branches are never constrained.
- **A `process-design` skill:** agents who propose a process must first assess its effect on research velocity. The
  skill also covers retiring processes, and there's no metrics script for now.

## The idea behind it

- A good process costs almost nothing while exploring and checks hard where a result is relied on: landing on `main`,
  publishing, citing, or handing off.
- It is enforced in code rather than prose, labels rather than blocks, keeps one source of truth, adds no file every
  lane must pass through, and has an owner and a retirement condition.
- Price a process in the scarce resources, not in steps: Daniel's attention, the merge path, files many lanes edit, the
  rules every agent reads, and pods.
- The evidence from last week's real changes:
  - root `AGENTS.md` changed 67 times, 25 of them on Sep 27;
  - the lane contract went from 2.0 to 2.4 in two days, one rule per incident;
  - PRs touching Lean take a median 4.7 h to merge, against 2.2 h for the rest.

## Needs your acceptance

- The skill makes the coordinator the owner of a weekly retirement pass over root `AGENTS.md` and the lane contract,
  using the skill's tests. Say who should own it; if nobody objects, it stands as written.
- The skill's PR (a three-line route in `AGENTS.md` under "Skills", plus `.agents/skills/process-design/SKILL.md`) is
  being opened as a draft. We'll post its link here.

## Suggested next step, not yet approved by Daniel

- Pilot the Lean-first norms on the one-stage audit, whose executable Lean already exists.
