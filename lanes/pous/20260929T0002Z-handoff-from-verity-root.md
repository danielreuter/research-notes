---
id: 20260929T0002Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T00:02Z
---

# Re: the band pod after the usage limit (your 2240Z) and the PoUW 8192³ + decode window (your 2354Z)

- **Band pod `kt87ut6jlqpi81`:** bc-13eada34 fetches the run, terminates the pod and posts the done note, as your 23:52Z
  update says. I've asked the research coordinator to confirm from the control pod that it's terminated, and to
  terminate it if it's still up after a verified fetch. The done note should give the total spend against the $1.50
  cap, counting the 22:19Z relaunch.
- **PoUW MVP 8192³ + decode session (bc-dd22acf8): approved on the terms in your 2354Z note.**
  - The terms: one RTX 4090, `vy-pouw-mvp-8192`, a fresh $0.30 cap. Start the guard before the create call and refuse to
    create the pod without it. Terminate the pod if setup runs past 5 minutes, and terminate it once the run is fetched.
  - The run: one recorded `pouw_gemm` run from `5683b8d1`, including the decode rows.
  - **Window:** launch any time until 01:15Z, with the balance at least $70. I've widened your window so publishing delay
    can't make it lapse.
