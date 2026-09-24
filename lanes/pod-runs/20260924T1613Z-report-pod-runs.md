---
lane: pod-runs
kind: report
created: 2026-09-24T16:13Z
status: open
---

CHECKPOINT 6d7728d5 (17:15Z) [open] guard E2E done on real pod: refused 17:01/17:09 while unfetched, self-terminated 17:10:36Z via pod key (GraphQL podTerminate); handoffs 1707Z+1712Z answered; writing FINAL
CHECKPOINT f5f58aaf (16:56Z) [open] guard+fetch marker committed f5f58aaf; real pod: launcher-kill mid-ship left nothing (pod removed partial), pod key != account key & reads 403; bootstrap run r20260924-165544-3013 + guard (idle 3) live on vy-pod-runs-test
CHECKPOINT none (16:41Z) [open] streaming ship committed 51f39598 (launcher 21 MB RSS mid-ship vs 640 MB before); building guard daemon + .fetched marker
CHECKPOINT 0b0768ed (16:13Z) [open] started 16:16Z at base 0b0768ed; read contract/brief; inbox empty. next: create cpu3c pod, baseline launcher RSS, streaming ship, pod guard

## What changed (lane/pod-runs, commits 51f39598..6d7728d5)

- `remote.py`: the source ship is streamed. One `git archive` pass computes the digest and manifest; a second is piped through
  `ssh -C` in 1 MiB chunks (`ssh_stream`). Every guarantee in the docstring still holds: digest and manifest compare,
  READY.json, SourceNotReady, no half tree executes. A killed launcher leaves a short stream, so the pod finds the digest wrong
  and removes the partial itself (trap). Partials untouched for 30 min are cleared by the next ship. The timeout is
  size / 64 KiB/s (at least 600 s). `git archive` runs with capped caches.
- `remote.py`: `fetch --all` is streamed too (`ssh_read`, extracted member by member). After verification it writes
  `<run>/.fetched` on the machine (research/fetched/v0.1, with `verified_from` = the machine's clock before hashing).
- `remote.py` + `pods/sh/pod_guard.sh`: the pod-side guard. A machines.toml entry opts in with `guard = N`, and `launch-request`
  then calls `ensure_guard`, which starts one daemon per pod (`pod_guard.sh daemon`, flock/pidfile). Each minute `guard_tick`
  decides busy / idle / refuse / terminate and writes `<root>/guard/state.json`. Termination uses only the pod's own
  `RUNPOD_API_KEY` from `/proc/1/environ`. Without that key nothing is installed and the launch prints `NO guard: ...`.
- `pods/workproc.py`: the work-process definition, now shared by the guard and the watcher's POD_PROBE. **notes.py diff is
  minimal** (steward edits it in parallel): one import line, plus the probe's regexes and prune list taken from workproc. The
  watcher now also ignores the guard's own processes and prunes `guard/` directories.
- `cli.py`: `fetch --all` says when the machine-side marker was not written.
- Tests: `test_pod_guard_daemon.py` (29: fake process tables, GPUs, clocks and fetch markers, the daemon loop, single instance,
  ensure_guard, the real terminate path against a fake RunPod API, streamed fetch memory) and 4 new tests in
  `test_remote_ship_source.py` (streaming memory, git-vs-memory manifest, launcher killed mid-ship).

## Handoffs received

- `20260924T1707Z-handoff-from-coordinator-guard-key.md`: the diagnosis in it was wrong. The key was in `/proc/1/environ`; the
  17:04Z failure was my bug (a pipe plus a heredoc on python's stdin gave it an empty key). Fixed in 6fa6124f. The pod then
  terminated itself at 17:10:36Z, so `/etc/rp_environment` was not needed. Replied in
  `lanes/coordinator/20260924T1714Z-handoff-from-pod-runs.md`.
- `20260924T1712Z-handoff-from-coordinator-suite.md`: the failures are pre-existing on main. The cli tree (e7d4a978, run
  read-only with PYTHONDONTWRITEBYTECODE=1) shows test_store_prov.py 3 failed / 45 passed and test_store_vllm_tools.py
  7 failed / 4 passed, the same as this branch. A base 0b0768ed export fails the same tests. /tmp/pod-runs is removed at FINAL.
