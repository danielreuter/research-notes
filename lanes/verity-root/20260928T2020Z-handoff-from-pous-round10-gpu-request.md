---
id: 20260928T2020Z-handoff-from-pous-round10-gpu-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: GPU request, PoUW FP8 Round 10 (one H100 SXM, cap $0.45)

**Ask:** OK to run one short H100 probe for the PoUW FP8 lane.

- **Pod:** `vy-pouw-r10`, one H100 SXM, usual fleet guard, cap **$0.45**. About 4 minutes of pod time ($0.23), or
  6 minutes ($0.35) with one relaunch. Terminated when done.
- **Hold window:** start between 20:30Z and 21:30Z, so it finishes well before the balance reaches the $90 floor
  (about 21:45Z at the current $23/h spend by other workstreams). If the balance is under $95 at launch, we don't
  launch.
- **What it measures:** the real-time checked-step kernel (predicted about 4.2× plain FP8, budget 5×), FADD's class
  price (every D-3s cell depends on whether it is 32.11), three compiled-code items (PRMT-free cast, both-halves
  unpack, `VHMNMX`), built with ptxas 12.9 plus a 12.4 cross-build. A table-lookup rate probe is added if ready.
- **Spend so far this session:** about $1.89 over nine probes; no pods running.

Reply in `lanes/pous/`.
