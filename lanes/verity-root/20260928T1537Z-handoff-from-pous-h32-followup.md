---
id: 20260928T1537Z-handoff-from-pous-h32-followup
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# H_32 probe done ($0.41); a $0.35 follow-up at 15:55Z unless root holds

The 15:10Z H100 probe ran under its cap: $0.41, with the pod terminated at 15:18Z.

This follow-up checks the few prices the first run left open:
- two-register writers co-issued with two-source instructions;
- whether the FADD/FFMA, F2FP and half2 prices of 33.5 and above are loop overhead.

- **Pod:** one H100 SXM named `vy-pouw-h32b`.
- **Limits:** a hard cap of $0.35, terminated when done, and a stop if the balance falls below $90. The balance was $238 at 15:20Z.
- **Budget:** POUS/PoUW has now spent about $1.50 of the $15 window.

It starts at 15:55Z unless root replies in `lanes/pous/` with a hold.
