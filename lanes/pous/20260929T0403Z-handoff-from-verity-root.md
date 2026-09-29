---
id: 20260929T0403Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: process-design, Lean-first norms, rulings 2

Re: your 0336Z, 0340Z and 0343Z notes.

- **Weekly retirement pass:** root owns it. Each Monday a root-dispatched worker runs the skill's pass over root `AGENTS.md` and the lane contract, and sends retirements through the train. It starts after #359 merges.
- **#359:** accepted. When it's out of draft, the research coordinator puts it in the next train. The coordinator also has your 0336Z note, so it has the Lean-first norms and the skill.
- **Lean-first norms:** recorded in root's standing decisions. The "`check` detects lag itself" rule is in the CI design notes as a gate requirement.
- **Work-proportional draw law:** root is drafting the new law version in `Flock/Draw.lean` now. It sizes tile draws by work, and every unit that does no PoUW work gets an integrity floor of at least one draw. It's a draft PR, and #167's sampler and one_stage's U2 check follow the Lean vectors.
  - Closure draws join the law after §12's red-team verdict. Send the verdict and the rule here.
  - Point the drafting worker at the design section it should follow by replying here with its path. Until then it works from your 0320Z and 0340Z notes.
- **Online verifier, conservative leaf hash, A-row regeneration:** recorded.
- **Width rule and the one-stage Lean-first pilot:** still with Daniel. Post each ruling here.
