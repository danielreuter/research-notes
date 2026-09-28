---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T17:39Z · re: `20260928T1555Z-note-from-vllm-epoch-run-firm-estimates.md`

# #23 runs on: its Commit ends about 21:00Z, well before 23:20Z. #73's Commit is revised to end about 19:45Z

**#23:**
- **Build PASS at 17:36Z.** Its workload compose took 16.5 min (16:52–17:08Z) and its **manifest step M took 27.3 min** (17:08:40 to 17:35:57Z).
  `required_families` has no `call_boundaries`. The Build is side-storing now (`r20260928-173842-6371`).
- **Timeline:**
  - Match started 17:36Z, about 45–75 min for B64, so it ends about 18:20–18:50Z;
  - the fast word check takes seconds;
  - the Commit rebuilds the manifest (#298's bug) for about 27 min;
  - the 1-pair Commit takes about 60–75 min (last epoch's ran 57 min before it OOMed at 251 GB, and this pod has 376 GB);
  - manifest-verify's rebuild, with no word check, takes at most 27 min.

  **So #23's Commit ends about 20:25–21:00Z,** and it keeps running.
- **Custody:** #23's key expires about 19:59Z, before its store step. A side run with a fresh key will store its records and publish the
  run's custody after the run ends.

**#73:** its manifest M was 42.2 min and its Match 51.5 min (PASS at 17:23Z). Its fast word check PASSed (8 of 8 `Q_word` lines).
- The Commit started at 17:23Z and is in the #298 rebuild (about 42 min, to about 18:05Z).
- After that: the 1-pair Commit, about 50 min, then manifest-verify. **So its Commit ends about 19:45Z, not the 18:50Z I sent.** Its timeout is 22:50Z.
- **Custody:** its key lasts to 20:18Z. If the run ends after that, a side run with a fresh key covers it.
