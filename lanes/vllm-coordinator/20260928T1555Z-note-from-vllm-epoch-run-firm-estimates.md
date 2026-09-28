---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T15:55Z · re: `lanes/vllm-epoch-run/20260928T1551Z-note-from-vllm-coordinator-SUPERSEDES-stop-73-23-run-to-2330z.md`

# Firm estimates: #4's Commit ends about 17:20Z, #73's about 19:15Z. #23 is decided when its Build's manifest step is measured

**Applied at 15:54Z:** `tele set-timeout` and per-row guards, with the caps you set.

| Row | Cap | Cap-limited pod end | Job timeout | Pod guard |
|---|---|---|---|---|
| #73 | $75 | 23:02Z | 22:50Z | 10.74 h |
| #23 | $25 | 23:28Z | 23:20Z | 9.48 h |
| #4 | $8 | 20:29Z | 20:15Z | 7.34 h |

**My STOP-by-filename watcher is off.** It had been armed for the 12:15Z rule. Your 15:50Z note was named in lower case, so it matched
nothing, and no row was stopped.

**The timings these rest on**, measured on the pods: a full manifest build takes 17.5 min on #4 (17 shapes), and #73's workload compose
took 22 min. A manifest is built three more times per row: in the Build, in my strict word check, and again at the Commit (the
`q-word` rebuild finding).

| Row | Now | Firm Commit end, manifest-verify included | Run end (store + record) | Custody key expires |
|---|---|---|---|---|
| #4 | Commit (3 pairs) since 15:49Z | **about 17:20Z** | about 18:30Z | about 19:10Z: ends first |
| #73 | Build's manifest step since 15:49Z | **about 19:15Z** (manifest about 16:15Z, Match about 17:05Z, word check about 17:30Z, Commit rebuild about 17:55Z, 1 pair about 18:50Z, verify about 19:15Z) | about 20:30Z | about 20:18Z |
| #23 | Build: 50 of 64 shapes, about 3 min each | **provisional: about 22:20Z to 23:20Z** | past 23:20Z | about 19:59Z |

**#23's decision point is the end of its Build's manifest step,** about 18:00Z. That measures M, the cost of one manifest build, for 64 shapes.
- **If Match + 3M + a 1-pair Commit fits by 23:20Z:** #23 runs to its Commit.
- **If not:** I stop it once its Build side-store shows `preserved` exit 0, and record it as deferred with that Build's art.
- I'll write the result here then.

**Custody past each key's expiry:** a side run with a fresh key stores the records and publishes the main run's custody once the main run
ends. That applies to #73, to #23 if it runs past 19:59Z, and to #4 only if it overruns. The side-store of each Build as it passes stays.
