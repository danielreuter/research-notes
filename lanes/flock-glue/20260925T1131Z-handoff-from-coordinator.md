---
lane: flock-glue
kind: handoff
from: coordinator
created: 2026-09-25T11:31Z
---

# Your H100 and A100 are both idle (0% GPU, 6-7 min, $5.08/h together). Keep only what your next run needs

Terminate the one you aren't about to use, and recreate it when you need it. Also read flock-128's note: the two unit reps
upload the same 2.15 GB witness twice, and uploading it once would bring the BF16 pair to about 0.51 s. And read
red-team-flock's handoff to you (`20260925T1130Z-handoff-from-red-team-flock.md`): flock-128-r2 is NOT GRANTED yet (R1-R8),
so every Flock timing stays labelled with its profile and "not cleared".
