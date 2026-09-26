---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-epoch
created: 2026-09-26T03:35Z
---
# BISECT #4 #23: both pinned at step 0 (records only; $0, no pod). Neither is a code change

## #4 smollm2-135m B16 (FAIL-class; the epoch Commit PASSes)
- **Check:** `verdict`. The expectation is `$.pass = false` only because `expected.pass = (class == "GREEN")` (`checks/verdict.py:50`).
  Every other check in `expected/<#4>.json` is `applies: false` ("Commit never closed", "no build_summary.json"). The v1 reference
  has **no Build, Match or Commit**: `test_regression.py:16` says "R17 row; only the CPU record audit exists".
- **Why the v1 row is FAIL:** its record audit
  (`art:c916a531…/_audit/audit-smollm2_l40s_b16_1024_128_int6/audit.json`) has `status: RED` with reasons "record checker != fast
  Match of record strictly: 4 difference(s)". All four are `global_program.digest_verification`: the record checker has
  `verified: false`, `why: "descriptor.json.gz not beside the artifact"`, and the fast Match has `verified: true` + descriptor sha. The
  archived GM-01 `global_match.json` itself says `verdict: PASS`, failed [].
- **Epoch run:** Build PASS, Match PASS (GM-01 PASS, fold True), Commit PASS (`r20260925-233854-c7c4` at `ad8050e9`; checks all
  PASS; `verdict.json` in `r20260926-020557-eb97` and the record `r20260926-015749-2654`).
- **Offending commit: none.** Nothing flipped in code. The FAIL label came from an incomplete v1 archive (a missing
  `descriptor.json.gz`), not from a Commit, and v1 never ran a Commit for this row.
- **Classification: test expectation.** Proposed re-baseline reason: "#4's FAIL class was the v1 record-audit RED
  (descriptor.json.gz absent from the archived record: digest_verification unverifiable); the row's first full run
  (Build+Match+Commit) passes." Changing a row's class is the owner's call, so it's a decision entry in fixtures.toml.

## #23 llama32-1b B64 (GREEN; the epoch Match has NO FOLD)
- **Check:** the Match stage (the `global_match_checks`/`verdict` table cells come from it). `match/stages.json`: `capture` **returncode -9**
  after 191.8 s (SIGKILL). The capture log ends normally, at "acquisition plan hooks installed beside the observer" and then
  nothing: no traceback. `control` then failed with "Free memory on device cuda:0 (20.9/44.39 GiB) … less than desired 0.5",
  because the killed capture's GPU memory had not been released yet. `fold`/`resolve` failed with `EOFError` on the truncated
  capture log. GM-01 ran over no fold, so the result is INCOMPLETE.
- **Why SIGKILL:** the host memory cgroup. `vyv-rf-epoch-moe67` has a 125 GB cgroup-v1 limit (`memory.limit` = 124,999,999,488, not
  the 1,007 GB host). The row_pod planner predicts #23's Match peak at **148,303 MiB** (my 20:40Z planner run), more than the
  119,209 MiB limit. The Commit was then refused by name for the same reason: F-dA-15 host retention 182,765 MiB > 119,209 MiB
  (`commit.log`). Neither my hold watcher nor the job cleanup sends SIGKILL (both send TERM, and only to `commit` stages). #11 was
  stopped by TERM at 20:59:39Z, before #23 started.
- **Offending commit: none.** It's the pod shape, not code: the v1 reference ran on a larger host.
- **Classification: expected behaviour of an under-sized pod (an environment failure), not a regression.** No re-baseline:
  #23 keeps its old GREEN expected. To confirm by GPU (not done; > $10 and > 3 h): Build + Match of #23 on a pod with a cgroup of at
  least 233 GB (the Build alone took 2.8 h).
- Evidence: `r20260926-021148-30ef` (small-file copy of the recording run: `sweep/<#23>/match/stages.json`, `match/logs/*.log`,
  `match.log`, `admission.json`), `r20260926-020557-eb97` (`row.log`, `commit.log`), planner in `lanes/vllm-rf-epoch/STATE.md`
  (20:40Z).

## Pods
All epoch pods are terminated (tp70 and tp70b at 03:17Z, after `r20260926-025813-4a23` / `-025815-7b60` were PRESERVED), and every
`vyv-rf-epoch-*` registry entry is removed. The bisect used no pod. Lane spend about $107 of the epoch's $130; bisect $0 of $10.
