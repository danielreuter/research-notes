---
id: 20260928T1835Z-handoff-from-pous-round9-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Round 9 H100 probe finished, pod gone, no further GPU work without asking

- **Run:** `r20260928-181753-0070`, one H100 SXM (`vy-pouw-r9`), 18:14:39Z to 18:19:06Z. The guard terminated the pod at its cap and the API confirms it gone (404). The guard and the pod-side backstop are both stopped.
- **Spend:** about $0.26 of the $0.30 cap, so about $1.89 over all nine rounds of your 1133Z window ($15). Balance read $170.19 after termination, above the $90 floor.
- **Result:** FADD's class price measured 32.11 again, above the FP8 candidate's threshold (about 32.02). The red team is repricing, and it may propose one more probe to decide whether 32.11 is real or a measurement bias.
- **Next:** any further GPU run comes to you first as a new note with a cap and a hold window.
