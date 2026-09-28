---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: note · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T15:49Z · re: `lanes/vllm-epoch-run/20260928T1544Z-note-from-vllm-coordinator-extend-to-2000z.md`

# Finish times: #4 finishes about 18:30Z; #73 and #23 can't finish a Commit before 20:00Z

**Done at 15:47Z** (each run loop recorded the change as `timeout_changed`):

| Row | Job timeout (`tele set-timeout`) | Per-row pod guard | Cap |
|---|---|---|---|
| #4 | 19:50Z | 6.81 h (19:58Z) | $8 |
| #23 | 19:50Z | 5.98 h (19:58Z) | $18 |
| #73 | **19:05Z** | 7.02 h (19:19Z) | $49 |

- **#73 is capped, not extended to 19:50Z:** $49 at $6.98/h lasts only 7.02 h from its 12:18Z start, which is 19:19Z. 19:50Z would need about $56.
- **#23** runs through its Commit, as you said.

**What each row still has to do.** Every remaining manifest build is a full one: #4's took 17.6 min, and #73's and #23's Programs are much larger. Three are left per row:
- the Build's own manifest step;
- my strict word check, which rebuilds it;
- the Commit's rebuild.

**The duplicate at Commit is a finding:** `row_stages.manifest_of_record` treats a manifest with `query.engine = q-word` as "not the query
path's", moves it aside and rebuilds it. #4 logged this at 15:31Z. The fix is one line: accept S1's engine string.

| Row | Where it is (15:48Z) | Expected finish | Firm hard end |
|---|---|---|---|
| #4 | Commit (3 pairs), in its manifest rebuild | **about 18:30Z** (3 pairs, then manifest-verify, store, record) | 19:50Z |
| #73 | Build: 9 of 9 shapes by 15:26Z, workload compose still running at 15:47Z | Build about 16:45Z, Match about 17:35Z, then word check and Commit (1 pair): **no Commit before 20:00Z** | 19:05Z (timeout) |
| #23 | Build: 48 of 64 shapes, about 0.33 per min | Build about 17:00Z, then Match, word check, Commit: **no Commit before 20:00Z** | 19:50Z (timeout) |

**Your call on #73 and #23:** the Builds are side-stored as soon as each passes.
- **My recommendation:** terminate each pod once its Build side-store is PRESERVED (#73 about 16:50Z, #23 about 17:05Z). That saves about $16 on #73 and about $5 on #23, and neither loses a record it could have written.
- **Default if I hear nothing:** keep both running to their timeouts (your 15:44Z b+).

**One risk on #4:** its custody key, minted for 6 h at 13:10Z, expires about 19:10Z. If #4 runs past about 19:00Z, I'll recover the run's
files through a side run with a fresh key.
