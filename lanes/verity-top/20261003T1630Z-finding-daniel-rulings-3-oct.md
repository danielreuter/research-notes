---
id: verity-top-20261003T1630Z-rulings-3-oct
campaign: verity
lane: verity-top
kind: finding
status: open
repo: verity
origin: root Project chat with Daniel, 2026-10-03
---
# Daniel's rulings, 2026-10-03 (until each lands in AGENTS.md or the friction skill)

- Label fallback: approved ("3. sure", root Project chat, ~15:27Z). Circuits records it as a line in .agents/skills/friction/SKILL.md in its label-fallback PR.
- PoUW may import sampled proofs (verity_sampled_proofs). Lean records it in #939.
- D = 0 pin: approved. Memory accounting's pin PR records it.
- Coordinator ruling (19:18Z): a PR whose head is an ancestor of main, left open only because its base was a feature branch, may be closed by its owner with "Merged into main at <sha> (check <id>)". To move into .agents/skills/friction/SKILL.md.
- Statement review replaced by a DM (lean thread, 2026-10-04 ~01:48Z = 3 Oct 6:48 PM PDT): lean proposed deleting the `queue.toml` rule that makes `research merge` refuse a spec change (a guarantee's statement, the definitions it reads, or a named assumption) until a reviewer signs off, and instead DMing Daniel when such a change lands on main, with nobody signing off and nothing waiting; it asked "a DM to you, or a channel?". Daniel: "DM to me." He then said "Let's get this new Lean rolled out ASAP." Confirmed by verity-top 05:30Z, 4 Oct. Implemented by #1053 (+ the DM in research merge).
