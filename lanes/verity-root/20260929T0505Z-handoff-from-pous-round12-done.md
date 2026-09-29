---
id: 20260929T0505Z-handoff-from-pous-round12-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Round 12 H100 probe finished, pod gone, no further GPU work without asking

- **Run:** `r20260929-044901-67d3`, done rc 0, SUCCESS, preserved. One H100 SXM, `vy-pouw-r12` (`va8aqm7mvnh68x`),
  with no relaunch.
  - The dead-man timer was confirmed alive before work started. The pod was drained at 04:50:02Z, before the timer
    fired.
  - GET returns 404 (04:50:05Z and 05:04Z), and no `vy-pouw-r12*` pod is left. Your fleet guard (pid 810209) never had
    to act.
- **Spend:** about $0.10 of the $0.20 cap (1 min 41 s at $3.49/h). The billed figure follows when RunPod posts it.
  - That makes about $2.55 over twelve rounds of your 1133Z window ($15).
  - The balance read $273.63 at 04:56Z, account-wide.
- **Result:** the H-1T checked-step kernel launched; the harness fix worked. It runs at 55.84% of the tensor-core rate,
  and 0 of 152,064 words differ from the reference replay. **H-1T's measured slowdown is 3.99× at 8,192³ and 3.97× at
  16,384³,** inside Daniel's 3–5× target, before transcript hashing.
- **Next:** any further GPU run comes to you first, as a new note with a cap and a hold window.
