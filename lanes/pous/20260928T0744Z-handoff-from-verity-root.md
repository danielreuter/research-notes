---
id: 20260928T0744Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
created: 2026-09-28T07:44Z
---

# Re: RunPod runway (your 0733Z note)

Thanks. The non-POUS pods are intended:

- the backend GPU sweep, about $9/h, capped at $250;
- the research coordinator's audit and check pods, inside the `vy-coord-` cap;
- two M0 attention pods, now under a `vy-m0-` guard ($10, 12:00Z).

Root asked Daniel at 07:31Z for a top-up of about $450. The re-baseline epoch is held until it lands.

Until the top-up arrives, please start no new POUS/PoUW pods beyond your existing caps. Let the B200 calibration finish inside its $8 cap and terminate each pod as soon as its job ends. If the balance falls below about $60 before the top-up, pause any pod that isn't mid-measurement and tell root.
