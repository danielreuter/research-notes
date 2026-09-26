---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-ir-lowering · kind: handoff · from: coordinator · created: 2026-09-26T16:30Z

# c2 can't publish: all three registrations are timing-contended

The three c2 registrations are art:82f4a9be, art:87a6bcdd and art:a43e5cac (unit `.../class-t129-256`). Each records
`protocol: {warm: true, runs: 5, contended: true}`. The published rules need uncontended timing, so the render rejects them
with code M, "protocol: … contended True (need warm, >= 5, uncontended)". That holds even for art:87a6bcdd, which
verify-flock-pure has already verified.

- **What to do:** re-run c2 so the timing guard passes, then register it once, with `--lane`. PR #72 sizes threads to the
  cgroup's CPU quota; check the pod really runs with that change.
- **Then:** label the three contended copies `superseded_by` the new one.
- **Where #101 stands:** C-Flock is at 56.9% with c1 and c3. c2 covers T = 129–256.
