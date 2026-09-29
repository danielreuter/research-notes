---
id: 20260929T0400Z-handoff-from-pous-round11-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Round 11 H100 probe finished, both pods gone, no further GPU work without asking

- **Runs:** `r20260929-033625-cb6e` (done rc 0, SUCCESS, preserved) and the first pod's partial `r20260929-032519-dff5`
  (preserved as an artifact).
  - The first pod (`31o6bzoz6a12he`) reached its 0.06 h age limit during the CUDA 12.9 fetch and builds. Our guard
    removed it at 03:28:22Z.
  - The one relaunch (`hkbke8aqd94pg5`) ran the series and was terminated at 03:39:04Z. Both GETs return 404, and no
    `vy-pouw-r11*` pod is left (checked again at 03:59Z).
  - The dead-man timer was confirmed alive on each pod before work started. Your fleet guard (pid 799443) never had to
    act.
- **Spend:** about $0.41 of the $0.45 cap ($0.215 and $0.193, by runtime × rate; RunPod's billed figure lags about an
  hour).
  - That makes about $2.45 over eleven rounds of your 1133Z window ($15).
  - The balance read $276.64 afterwards, account-wide.
- **Results:**
  - H100 FP8 word captures: all 4.9M words match the reference model, which closes the Lean model's silicon condition.
  - The honest FP8 checked step clears Track C's 5× threshold on one run (52.67 per add word, against 52.73).
  - SHAKE256 is 2,291 units per byte and TurboSHAKE128 826; these feed Daniel's A6 note.
  - One harness bug (a shared-memory attribute) kept the H-1T step kernel from launching, so its timing is still open.
- **Next:** any further GPU run, such as re-timing the H-1T step, comes to you first as a new note with a cap and a
  hold window.
