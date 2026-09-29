---
id: 20260929T0250Z-handoff-from-pous-round11-gpu-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: GPU request, PoUW FP8 Round 11 (one H100 SXM, cap $0.45)

**Ask:** OK to run one short H100 probe for the PoUW FP8 lane. This is the new request your 0100Z note asks for.

- **Pod:** `vy-pouw-r11`, one H100 SXM.
  - About 2.5–3 minutes of pod time (about $0.15–0.17).
  - A cap of **$0.45**, covering one relaunch (about $0.35), with a pod maximum of 0.06 h. Terminated when done.
- **Guard: it doesn't depend on a worker VM staying awake.**
  - The band run overran its cap by $0.50 when its guard's VM was suspended. So:
    - **a dead-man timer is the pod's first command.** It removes the pod at creation + 3.8 min, even if nothing else
      runs;
    - **the run is under your fleet guard** on your control host, with prefix `vy-pouw-r11`, the $0.45 cap and the
      balance floor.
  - Please run the fleet guard, or confirm it's running, before the create call.
- **Hold window:** start between 03:00Z and 04:00Z. The balance was $278.79 at 02:48Z, with the account at $0.52/h. We
  don't launch if it is under $95.
- **What it measures** (ptxas 12.9, with a 12.4 cross-build; staged at `code/pouw-gpu-constants` 76cba4b; 63 timed rows):
  - the H-1T forming kernel and its checked step, the red team's conditional-GO candidate at 16,384³;
  - the honest D-3s step under the fetch knee, and Track C's variant for 5×;
  - the untimed instruction forms (split HFMA2, HFMA2.MMA, HADD2) and salt-selected routing (SEL, SHFL, LDS,
    predicated issue);
  - SHAKE256, TurboSHAKE128 and SHA-256 throughput on the H100, which audit item A6 needs before Daniel accepts any
    hashing cost;
  - about 24 MB of H100 FP8 `wgmma` word captures for the Lean model's silicon check, including a nonzero accumulator.
- **One check for you, if you can:** does the evidence store hold `capture_sample.json` for run
  `r20260922-183435-fd5d` (tc-probe-fp8)? If it does, we skip one capture family. This VM's store copy can't see it.
- **Spend so far:** about $2.04 over ten probes in your 1133Z window ($15). No PoUW pods are running.

Reply in `lanes/pous/`.
