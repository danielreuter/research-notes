---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (firm estimates, a default, one choice) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:43Z

# #74, #67 and #68 can't finish their Commits by 23:20Z. By the standing rule, each stops after its Build is stored. #70 may fit.

**How I estimated:** from #73's measured stages (same code, 1 pair, 2× H100):
- the Build's `required_manifest` took 42 min;
- the Match took 51.5 min;
- the Commit took 146 min: 43 min of `prepare`, which is almost all the Commit-time manifest rebuild, then 80 min of delta and validate;
- the store took about 8 min.

This epoch's Builds run far longer than `rows.json`'s old estimates (#74 said 5.4 h in total, and it's 4.6 h into the Build).

| row | now (20:43Z) | Build ends | Match ends | Commit ends | fits 23:20Z? |
|---|---|---|---|---|---|
| #74 (2× H100, 1 pair, $6.98/h) | `build.required_manifest` since 20:32Z | ~21:15Z | ~22:07Z | ~00:30Z (the cap runs out ~23:03Z) | no |
| #67 (2× L40, 3 pairs, $1.64/h) | `build.global_program` since 20:29Z | ~21:35Z | ~22:20Z | ≥ 23:35Z (the manifest rebuild alone runs to ~23:03Z) | no |
| #68 (2× L40S, 1 pair, $2.18/h) | deriving request 28 of 32 | ~22:00Z | ~22:45Z | the manifest rebuild alone runs to ~23:30Z | no |
| #70 (2× L40S, 1 pair, $2.18/h) | `build.global_program_r0/r1` since 20:39Z | ~21:15Z | ~21:30Z | ~22:30Z | yes, **if** its manifest is complete |

- **#70 is a TP2 MoE row, like #75.** If its Build's `build manifest rc=` line shows `complete False` or unbound TP peer bindings, its
  Commit will refuse, as #75's did. I'll tell you the moment that line appears (about 21:15Z).

**Default (the 15:52Z rule):** at each Build's end, `side_store.sh N` stores the Build (the follow-up's seed if the tree hasn't moved).
Then I terminate the pod and record the row as deferred, keeping its old record. This saves about $12 on #74, and about $3 each on #67
and #68.

**The choice:** do you want #67 and #68 to run their Match before stopping? That's about 45 min each, roughly $1.2 to $1.6 per row, and
gives GM evidence for the follow-up. #74's Match would cost about $6. Without an answer by each Build's end, the default applies.
