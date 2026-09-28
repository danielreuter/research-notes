---
id: 20260928T2159Z-handoff-from-pous-round10-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Round 10 H100 probe finished, pod gone, no further GPU work without asking

- **Run:** `r20260928-205054-f167`, one H100 SXM (`vy-pouw-r10`, pod `89bkpuip2uew2v`), 20:50:30Z to 20:53:03Z.
  - It finished rc 0 SUCCESS and is preserved in the evidence store.
  - `research pods drain` terminated the pod at 20:53:03Z. The API returned 404 at 20:53:03.7Z and again at 21:57Z.
  - The guard and the pod-side backstop are both stopped.
  - The start was inside your 20:30–21:30Z window. The hold check at 20:50:26Z found nothing from you after your 2032Z note.
- **Spend: $0.1484 of the $0.45 cap,** billed by RunPod at 153.074 s × $3.49/h (per second, from
  `/v1/billing/pods`). That makes about $2.04 over all ten rounds of your 1133Z window ($15).
  - The balance was $113.17 before the create call, above the $95 floor, and $112.85 after termination.
- **Fleet sweep (21:04–21:57Z):** no idle `vy-pous*` / `vy-pouw*` pod, and nothing terminated.
  - The only one seen is `vy-pous-band-e2e-veritor-campaign` (L40S, created 21:55:22Z). It matches your 2132Z approval
    of the band-codec vLLM run and was left running.
  - `vy-pouw-mvp-8192` never appeared in any sample up to 21:57Z.
- **Result:**
  - FADD's class price is 32.00 for loops that fit in the instruction cache; the old 32.11 was instruction fetch in long
    loops.
  - The fast-checking track (Track C) is negative: 55.44 per add word, above the 53.18 it needed.
  - The FP8 target at 16,384³ now turns on whether the honest loop fits under that cache limit.
- **Next:** a possible Round 11 (H-1's forming kernel plus the honest-loop variants; about $0.15–0.20, cap ≤ $0.45) will
  come to you first, as a new note with a cap and a hold window. It will not come before the scheme's F19-2 repair lands.
