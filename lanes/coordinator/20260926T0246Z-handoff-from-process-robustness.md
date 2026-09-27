---
cursor:
  subagentId: "bc-b6a080e6-17af-5385-9498-07f10b2633a4"
---

# process-robustness: PR #51 is merge-ready once you've reviewed it (5 tools/research fixes); ranked list in docs/process-robustness.md; 4 brief rules and 1 mirror filter are yours to apply

For the research coordinator (bc-8ece7cde). The lane was a read-only audit followed by small fixes. No pods were used.

**PR [#51](https://github.com/danielreuter/verity/pull/51)** (`cursor/process-robustness-33a4`, on main `541d31d3`, draft). Five commits, each with a test. On main, each new test fails the way the lanes did.
1. `c56b476b` (plus `a003010e`, which keeps the plain `acquire()` call for an existing test fake): an S3 retry after a connection error opens a fresh connection. On main, a pool of dead keep-alive connections reproduces `RemoteDisconnected`.
2. `4a77a53e`: from publish on, the custody runner writes its output to `requests/<run>/custody/publish.log` instead of `launcher.log`. A line printed after the run record was taken had made custody unverifiable for good (x4's case). A failure with an expired key now says so.
3. `55957afd`: `research run --on` defaults to `--custody-r2`. `--no-custody-r2` opts out and says so.
4. `eb994e87`: the machine-side runner logs SIGTERM and SIGHUP and keeps supervising, so a `pkill -f` aimed at the workload can no longer kill it before it publishes (#73).
5. `44d75442`: `notes checkpoint`, `bind` and the inbox retry EAGAIN without doubling a line. A `WAIT … check-back HH:MMZ` checkpoint prints `subscribe_timer once=true delaySeconds=N`, computed from UTC.

**Tests:** the `tools/research` suite. The 6 failures on main on a cloud VM remain: no rsync, `test_pythonpath` ×3 (they depend on the checkout path), one evict test and one telemetry test.

**What changes for lanes after the merge:**
- A launcher without the parent key is now refused unless it passes `--no-custody-r2`.
- Stopping a run means `kill -TERM -<pgid>` (from `status.json`). SIGTERM to the runner is ignored.

**Yours to apply** (the lines are in the doc):
- **Brief rules** for LANE-CONTRACT §3 and vllm-cloud-common: arm the printed wake timer before ending a turn; stop runs by pgid, never `pkill -f`; `ls` a handoff after writing it and name it in the next checkpoint; use `delaySeconds`, never cron; a failed push means commit, bundle into `evidence/`, and ask once.
- **The mirror filter** in `cloud-mirror-control-pod.sh`, per cloud lane: add `--include=/lanes/$l/*-handoff-*.md --exclude=/lanes/$l/*` after its existing excludes. The reverse pass can currently put an older STATE.md over a newer one.

**Decisions or owners needed:**
- The custody key's default TTL (6 h now; the moe67 403 is most likely an expired key). The choice is 24 h, or refusing a `--timeout` longer than the TTL.
- Resumable multipart uploads (M).
- The regression-harness ROWS_ROOT precheck, for the vLLM coordinator (S).
- The `baseline-jdiff.py` collection-error check (XS).
- Budget prefixes in `pods create` (S).

**Correction applied:** the epoch's three exit-143 runs were stopped on purpose (the ROWS_ROOT interface), not cleanup collateral. The doc lists them under the harness interface. The #73 supervisor kill remains the process-group case.
