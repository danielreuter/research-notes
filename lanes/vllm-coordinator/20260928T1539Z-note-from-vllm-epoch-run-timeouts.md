---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T15:39Z

# Timing: #23 won't reach its Commit before its 17:42Z timeout; #73 and #4 are tight. I'm side-storing each Build as it passes

I hadn't budgeted the strict word check: it took 17.6 min on #4.

| Row | Where it is | Projection | Its job timeout |
|---|---|---|---|
| #4 | Commit (3 pairs) since 15:31Z | a 3-pair Commit of B16 may not fit | 17:20Z |
| #73 | Build (9 of 9 shapes derived) | Match about 51 min + word check about 17 min + Commit (1 pair) about 45 min ends about 17:40–17:55Z | 17:50Z |
| #23 | Build (45 of 64 shapes, about 0.58 per min) | Build ends about 16:20Z, then Match, word check and Commit | 17:42Z |

For #23, the Commit can't finish by its timeout.

**The safety net:** a timed-out job never reaches `epoch_row.sh`'s store step, so `side_store.sh` stores the Build from a separate
short run with its own custody key. #4's is uploading now (`r20260928-153814-5996`, 820 MB). #73's and #23's follow as each Build passes.

**Your call on #23:**
- **(a)** keep it running for the Build and side-store, then terminate it about 16:25Z. That costs about $0.7 more, and the follow-up epoch gets a Build.
- **(b)** let it run to the timeout, in case the Match is fast, for about $2.3 more.

Default if I hear nothing: (a).
