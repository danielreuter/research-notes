---
id: 20260928T2132Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-28T21:32Z
---

# Re: the PoUW 8192³ timing run (your 2103Z) and the band-codec encoded vLLM run (your 2120Z)

- **PoUW MVP 8192³ run (bc-dd22acf8): approved.** One RTX 4090, `vy-pouw-mvp-8192`, fleet guard, cap $0.30, pod
  terminated once the run is fetched. Launch now; your window closes at 21:35Z. The last reported balance was $106.94
  at 21:15Z. Keep your own rule: don't launch if the balance is under $95. If you miss the window, send a new request
  rather than launching late.
- **Band-codec encoded vLLM run (bc-13eada34): approved, with a launch condition.** One L40S, up to 60 minutes, hard
  cap $1.50, `research run --campaign pous`. Terminate right after the verified fetch, then send a done note. Launch only
  after the `--codec` change passes on CPU. It counts against the POUS $15 window.
  - **Balance floor:** $90 while tonight's vLLM epoch rows or merge trains are still running, which should be until
    about 3:45 PM PT (22:45Z). The fleet is burning about $20/h, so the balance will likely pass $90 around 22:05Z.
    If so, wait until the epoch rows and trains have ended. After that, the floor is $70.
  - Stop the run if the balance drops below whichever floor applies.
