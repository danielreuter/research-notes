---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff (final) · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T23:59Z · re: `lane-briefs/vllm-epoch-run.md` "Out"

# The epoch is over: one row written (#73), the rest deferred with their old records. Spend about $145 of $250.

**The digest table:** `internal/lanes/vllm-coordinator/20260928T1410Z-epoch-digests.md`, with the full digests and stored art ids in
`20260928T1410Z-epoch-digests.json` beside it. Here are the three lines added last, verbatim:

~~~text
| #70 | 432edb3b | 947b32e706e7fb92 / 0 req (-) / - | 394b581fb4f5bfda | - | 28a0beb4a9087b8a (+15) | -, word check fast PASS, deferred: Match for evidence (FAIL class: tp2 PASS, fold FAIL); Build manifest incomplete (13888 unbound TP peer bindings), no Commit; Build art:82931d60, records art:c8d (1 pair, time fallback: n_runs 6 -> 2) | r20260928-201320-6851 (secure, 2x NVIDIA L40S, 142 SMs, 128 vCPU, driver 580.126.09) | 3.95 |
| #67 | 432edb3b | 00ffdfc33f2e2b35 / 33 req (1e9e09cf7f8f74b4, ...) / 0ced77aa226ad5a2 | - | - | - | -, word check fast PASS, deferred: Match PASS for evidence (GM PASS, tokens equal, fold PASS); Commit refused 'required-value manifest not built (B=32)'; Build art:7fcbd092, records art:fd58eb69 | r20260928-161923-0a05 (secure, 2x NVIDIA L40, 142 SMs, 256 vCPU, driver 580.178.04; 1 offer(s) refused) | 11.79 |
| #68 | 432edb3b | - | - | - | - | -, word check not reached, deferred: Build PASS; Match cut by the run timeout 23:21Z (watcher paused), no store: Build NOT stored, pod gone; rebuild in the follow-up; old record kept (1 pair, time fallback: n_runs 6 -> 2) | r20260928-183104-1d90 (secure, 2x NVIDIA L40S, 142 SMs, 256 vCPU, driver 580.178.04; 1 offer(s) refused) | 10.88 |
~~~

## Per row

| row | outcome | why | stored |
|---|---|---|---|
| #73 | **written** (`e2914bd4` + `ff840ea8` on `cursor/epoch-run-expected-2622`) | PASS; rule (a): the GM fold pins moved, coverage is pending the `coverage.py` fix (the #325 check passes: ok, 315,912 checked, 0 missing) | Build `art:91fac396`, records `art:da7b7474` |
| #4 | deferred (held for audit) | Commit PASS on a FAIL-class row | Build `art:84ec56f4`, records `art:013671cf`, large `art:b604b4df` |
| #23 | deferred | NOT_RUN: the Commit's host admission refused it (483 GiB predicted, the pod has 351 GiB) | Build `art:7a30ced1` / `art:1c659f5e`, records `art:07062ee9`, large `art:b2b6ae9e` |
| #75 | deferred | NOT_RUN: the Build's required manifest is incomplete (12,480 unbound TP peer bindings, MoE two-producer sites) | Build `art:8f0d249a` / `art:72ee5851`, records `art:bef9f84c`, capture `art:bf21420f` |
| #70 | deferred | the same as #75 (13,888 unbound); the Match ran for evidence (the FAIL class's result) | Build `art:82931d60`, records `art:c8dc14fa`, capture `art:d4d50ffa` |
| #74 | deferred | stopped after its Build: the manifest requires `call_boundaries` (wave 2) | Build `art:39d08c35`, records `art:955cb90a` |
| #67 | deferred | the Match PASSED for evidence (GM PASS, tokens equal); then the Commit refused: "required-value manifest not built (B=32)" | Build `art:78548e75` / `art:7fcbd092`, records `art:fd58eb69` |
| #68 | deferred, **with the Build lost** | the Build passed at 22:47Z, but my VM was paused from 22:47Z to 23:52Z (the usage limit), so the stop-after-Build watcher never fired. The Match ran until the run's 23:21Z timeout, which killed it before its store; the pod is gone. The follow-up epoch must rebuild it. | only `evidence/` (run_record `art:4a7973ec`) |
| #101 | deferred after 5 tries | try 5 on #321: G3 now passes, G4 fails by 32 (the top-p selects) | Build `art:0e6911da`, records `art:55029fe0` |
| #60 | deferred, never launched | no 2× shape came before 19:20Z | - |
| #11, #39, #57 | not run today (deferred by the plan) | - | - |

## Spend

**$145.07** across 13 pod runs: #73 $55.05, #74 $36.97, #67 $11.79, #68 $10.88, #75 $9.78, #23 $8.50, #4 $4.84, #70 $3.95, and #101 $3.31
over 5 pods. Every row stayed inside its cap.

#67's and #68's pods were terminated while my VM was paused. RunPod no longer knows them, so I count them to 23:30Z, the `vyv-` guard's
deadline. If they ran until my watcher noticed them gone at 23:52Z, the total is at most $146.51.

## Open

- **The coverage backfill** (your 2031Z handoff) waits for #325 on main; main is `5810574d` and doesn't have it yet. Then there's one commit per row in
  `evidence/coverage-backfill.tsv` (#73 only). #73's #325 result is at `/workspace/epoch-evidence/73/coverage-325/` on the VM.
- **The canary re-pin** (`ops/known_roots.json`, cc 8.9) isn't done. No wave-1 row reached a clean end that could pin it.
- **Tooling that's now in `evidence/pod-scripts/`:**
  - `side_record.sh`: a regression record with the frozen v1 reference in reach.
  - `write_row.sh` and the rule (a) gate in `gate_write.py`: the write step, and the new write rule.
  - `stop_after.sh`: stops a row after its Build or its Match.
  - `store_build.sh`'s `capture` kind: a TP row's capture files as one tar.
- **Lessons for the follow-up epoch:**
  - Both TP2 MoE rows' manifests leave the TP peer bindings unbound (the `two producers` MoE sites). A TP2 MoE row can't commit until that's fixed.
  - Builds run about 3 to 4 h, not the old estimates.
  - A watcher on the VM stops when the VM sleeps. A stop that the epoch's line depends on belongs on the pod, not on the VM.
