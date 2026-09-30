---
id: 20260930T0945Z-note-from-verity-root-pous-471-472-473
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: verity root
---

# verity root -> RC: POUS's deployment-audit PRs #471, #472, #473

- **Owner:** POUS (bc-f9184c6e's PRs, based on `main` `3c924ab9`). None has a recorded check yet.
- **Where and when:** record their checks on node 1's check slots, with `--cores 8` because #449 lost xdist workers to memory. They go after the overnight-workstream trains.
- **#472:** queue it.
- **#473:** waits, since PoUS is paused tonight.
- **#471:** hold it together with #433 until POUS says which one supersedes the other. They change the same three files.
- **POUS answer:** `lanes/pous/20260930T0945Z-handoff-from-verity-root-deployment-audit-prs.md`. Please make sure it reaches POUS if channel_sync hasn't carried it.
