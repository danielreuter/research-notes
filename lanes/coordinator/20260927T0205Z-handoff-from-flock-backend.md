---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-27T02:05Z
---

# Two-hour same-DC attempt over: none of the 9 total-unit cells ran. No pods are running; about $6 spent of $25

- **Attempts, 00:17Z–02:00Z:**
  - **00:17Z EU-NL-1:** L40S plus H100. Stopped at your 00:32Z note and terminated.
  - **00:50Z and 01:13Z EU-NL-1:** L40S plus a CPU verifier. No route: CPU pods get no global-network interface (01:20Z
    note).
  - **01:16Z–02:00Z:** L40S plus the cheapest GPU verifier in the same DC. L40S capacity appeared in EU-NL-1, OC-AU-1,
    US-TX-3 and US-TX-4, but no second GPU from RTX 2000 Ada … PRO 6000 was available there, so each prover was
    terminated at once.
  - Across the whole evening, only one same-DC pair ever routed: EU-NL-1 L40S plus H100 at 21:36Z, which the pre-#91
    check refused.
- **What stands:**
  - The total unit is granted and gated on L40S provers (r20260926-213915-70e3, r20260926-224635-973c).
  - One cross-DC diagnostic cell exists (art:04688422).
  - Branch at 8e0d0adb (main e93da678).
- **For the next try:**
  - **(1) Allow an H100 or B300 verifier in EU-NL-1.** That was the only second GPU there tonight. At $3.49/h it costs
    about $3–4 for a 1-hour queue, still within the cap. It is also the only same-DC pairing seen to route.
  - **(2) Retry in daytime US capacity**, when US-TX-3/4 or US-MO-1 have both an L40S and a cheap GPU.
  - Either way it's one command: `/tmp/fp/total-dc.sh`, or `launch.sh l40s` with `GATE=1`.
