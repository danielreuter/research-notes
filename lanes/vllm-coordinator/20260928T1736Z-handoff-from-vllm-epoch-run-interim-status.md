---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (interim: the brief's 17:45Z point; the window now runs to 23:30Z) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T17:36Z

# Interim status: 0 written so far, 5 rows running, #4 deferred for audit, #101 deferred after 3 tries; about $66 spent

**Digest table:** `internal/lanes/vllm-coordinator/20260928T1410Z-epoch-digests.md`, with its JSON beside it
(`20260928T1410Z-epoch-digests.json`). It has lines for #4 and #101 so far.

| Row | State | Evidence and cost |
|---|---|---|
| #4 | **deferred:** Commit PASS on a FAIL-class row, for audit (your 16:53Z). Pod terminated 17:36Z | Build `art:84ec56f4…` (side-store `art:876db263…`), records `art:013671cf…`, large files `art:b604b4df…` (`instances.jsonl`, `accesses.jsonl.gz`, `program.json`), regression record in side run `r20260928-165832-8cc0`; custody PRESERVED; $4.84 |
| #101 | **deferred** after 3 Build FAILs, each a registration gap for #231's sampler: codec alias (fixed by #288), `NvLogf_v1` (#297), then `GumbelTopPTokenSelect_v2` in the program view | handoffs 1410Z, 1530Z and 1635Z; $1.39 |
| #73 | Match (Build PASS 16:31Z, Build side-stored `art:1b29fa7f…`) | $37 of $75 so far; Commit end about 18:50Z |
| #23 | Build: workload compose since 16:52Z; its manifest step decides | $6 of $25 |
| #74 | Build (`432edb3b`, 1 pair) | $11 of $49; end about 21:55Z |
| #75 | Build (3 pairs) | $3 of $12; end about 20:40Z |
| #67 | Build (3 pairs, 2× L40) | $2 of $13; end about 21:50Z |
| #60, #68, #70 | polling. #60 is held by the balance test (about $21 of headroom against its $24 cap); #68 and #70 need a 2× shape (#70's has to be cheap) | — |
| #11, #39, #57 | deferred (your rulings) | — |

**Found and fixed in the lane's tooling** (none affects a digest):
- **`rebaseline run` collected no tests:** it filtered with the full row key, but the test ids are `<tier>-<check>-r<number>`. The running rows
  carry the old filter, so each gets its regression record from a side run (`side_finish.sh`) before `write`. Rows launched from now on
  carry the fix.
- **Custody checks from the VM** read back every object by default, and a 60,000-file records tree takes hours. The check now takes each
  run's pod-side `.custody` marker plus each tree's `data put --preserve`.

**Spend:** $6.23 on finished rows plus $59.37 running, so $65.60, within the $250 cap. The final handoff comes when the last row
ends (by 23:20Z).
