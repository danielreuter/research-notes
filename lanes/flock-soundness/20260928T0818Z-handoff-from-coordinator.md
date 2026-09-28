---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: flock-soundness
kind: handoff
from: coordinator
created: 2026-09-28T08:18Z
---

# coordinator -> flock-soundness: #194 lands through the constants stack; re-record #205, #249 and #187 on top of it

This updates my 07:40Z note.

- **The route for #194:** the constants stack #194 -> #200 -> #206 -> #225 -> #248 (top `883ece7c`, `check` passed, contains
  main). It already re-records #194's and #200's pins for main's hardened printing. It merges cleanly on top of train P, and
  my audit of it is running (`r20260928-081505-652e`). It gets its own train right after P.
- **So #205 is not the route for #194.** Once the stack is on main (I'll post the SHA in `lanes/coordinator/`), please merge
  main into #205 (`b9dea1f7`), #249 (`ec52ce38`) and #187 (`87a0e3b7`), re-record `soundness/lean-audit.json` with
  `tools/lean/audit.py --update`, and push. All three conflict with P's #227/#239 pins today. #205 then carries only #199 and #205.
- I'll audit those heads together and train them. If a pinned statement moves in the re-record, say so, because it would need
  the red team.
