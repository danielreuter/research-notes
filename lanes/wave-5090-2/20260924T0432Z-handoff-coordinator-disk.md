---
lane: coordinator
kind: handoff
to: wave-5090-2
created: 2026-09-24T04:32Z
---
# coordinator -> wave-5090-2: laptop has 8.2 GB free and your /tmp/w5090-2 holds 1.5 GB -- put, then delete, as you go

Below 6 GB free the laptop guardian SIGKILLs the largest lane process (it killed two `research` commands that way at
00:46Z/00:53Z), and a full disk takes Cursor -- and every lane -- down with it. Keep at most ~1 GB staged on the laptop:
`research data put ... --preserve` each tree, confirm `research data preserved`, then delete its staging copy before
pulling the next. Don't pull whole verifier session stores: tar only the records you cite (as wave-h100-2 did, 200 kB).
