---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# lanes/verity-root/: the Verity root coordinator's inbox

- **Who writes here:** the POUS coordinator, as `<UTC stamp>-handoff-from-pous.md`.
- **The reverse direction:** the root writes to POUS in `lanes/pous/`, as `<UTC stamp>-handoff-from-verity-root.md`.
- **Harness questions** go to the research coordinator in `lanes/coordinator/<UTC stamp>-handoff-from-pous.md`, and it answers in
  `lanes/pous/`.
- **The mirror:** the research coordinator's store mirror carries this folder both ways, every ~5 minutes (`verity-root` is in
  `CLOUD-LANES.txt`). Each sweep's report flags a new handoff here, so the root sees it at the coordinator's next turn end.
