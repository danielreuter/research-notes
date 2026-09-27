lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-27T04:08Z

# PR #100: re-recording check at 4644cd3c as r20260927-040738-6b92 (r20260927-034707-b228 failed 4 pod-only tests, fixed)

- **r20260927-034707-b228** (617247f4) got past collection; 4 tests failed only on the pod: two store tests assert read-only by
  `os.access` (root passes it on 0444 files), and two runner tests inherited the recording run's `RESEARCH_SOURCE_SHA` and
  `PYTHONPYCACHEPREFIX` in their own nested runs.
- **Fixed at 4644cd3c** (main 3040ac1f merged): mode-bit checks; check's steps drop `RESEARCH_*` and `PYTHONPYCACHEPREFIX`. All four
  pass under those conditions locally.
- **Now:** r20260927-040738-6b92 on vy-circuit-checks-cpu3, expected about 04:45Z. The attempt id follows when it passes.
