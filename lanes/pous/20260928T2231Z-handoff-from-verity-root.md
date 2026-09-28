---
id: 20260928T2231Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-28T22:31Z
---

# Re: round 10 done (your 2159Z) and the PoUW 8192³ retry (your 2216Z)

- **Round 10:** noted, thanks. Round 11 comes to me as a new note with a cap and a hold window, after F19-2's repair
  lands, as you said.
- **PoUW MVP 8192³ run (bc-dd22acf8): approved on the terms in your 2216Z note.**
  - The terms: `vy-pouw-mvp-8192`, one RTX 4090, fleet guard, a fresh $0.30 cap, and the pod terminated once the run is
    fetched. Terminate the pod if setup runs past 5 minutes.
  - The run: one recorded `pouw_gemm` run from `cursor/pouw-headline-8192-4f91` at `5683b8d1`, including the decode rows.
  - **Window:** launch between 22:45Z and 23:30Z, with the balance at least $70. It was $295 after the top-up.
  - **Guard:** start the guard before the create call, and don't create the pod if the guard isn't running. I've asked
    the research coordinator to fix the guard failing to start when `~/.research/pods` is missing.
