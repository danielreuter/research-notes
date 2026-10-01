---
id: 20261001T0730Z-handoff-from-proofs-750-is-a-deadline-not-a-stop-proofs-verify-overlap
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# 7:50 AM PDT is a deadline, not a stop

Daniel, 12:22 AM PDT: nobody stops before he wakes (about 9:20 AM PDT). 7:50 AM PDT is the deadline for the overnight set.

- **Order unchanged:** build the session preflight, put its run spec in `lanes/proofs/`, and submit the confirming K=2048 run
  on the research owner's yes. Past 7:50 AM PDT (14:50Z), keep going: the session at K = 4096, 8192 and 16384 (one preflight
  per K), then the how-to that lets bf16-hill and flock-fp run their points in sessions. Stop only when that list is done,
  and then write here what you'd run next.
- **Node 1's window still holds:** nothing submitted after 5:05 AM PDT (12:05Z) that could run past 5:35; `/workspace` is
  offline 5:40–5:55. Resume at 5:55 AM PDT (12:55Z).
- **Anything that needs Daniel:** write it in `lanes/proofs/` as `needs-daniel:` with your recommendation, and carry on.
