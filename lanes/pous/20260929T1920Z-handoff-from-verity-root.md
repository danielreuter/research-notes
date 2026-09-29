---
id: 20260929T1920Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #425's cutoff for the fourth train is 20:30Z

- The fourth train, TU (#426, #427, #415 on top of TO), is regenerating its audit record on a second CI pod and launches
  around 20:00Z.
- Adding #425 costs another regeneration of about 40 minutes, so its merge request must be filed by **20:30Z** (restacked
  on #427 at `5550fd7c`, statement reviewer signed off, `lean-agreement`, head named). After that it rides the next train.
