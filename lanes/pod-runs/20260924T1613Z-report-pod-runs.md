---
lane: pod-runs
kind: report
created: 2026-09-24T16:13Z
status: final
---

CHECKPOINT 6d7728d5 (17:18Z) [final] tip 6d7728d5: streamed ship (launcher py 18-40 MiB vs 611 MiB), streamed fetch --all + .fetched, pod guard via pod-scoped key; real pod refused 17:01/17:09 unfetched, self-terminated 17:10:36Z (GraphQL); suite 327p/4s/12 known-fail
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

## FINAL

~~~text
tip: lane/pod-runs @ 6d7728d5 (base main@0b0768ed)        merge-with: none
known-failures: test_pythonpath.py 2, test_store_prov.py 3, test_store_vllm_tools.py 7 (sparse tree; the same on base 0b0768ed and main e7d4a978)    pod: terminated 17:10Z (by its own guard); $0.12
artifacts: none (evidence text in lanes/pod-runs/evidence/)
~~~

Tests at the tip: the tools/research suite, run file by file, gives 327 passed, 4 skipped, 12 failed. All 12 are the
known-failures above (they load integrations/vllm, tools/tc_probe and backends/sp1, which are absent from this sparse tree).
33 of the passing tests are new.

Launcher memory (`/usr/bin/time -l`, `research run --on --source .` of this 229 MB repo):
- Before: 611 MiB, and the launch timed out at 600 s (evidence/rss-before-launch.log).
- After: the launcher's Python holds 18-22 MiB during the ship (sampled over 17 min) and peaks at 40 MiB in the manifest pass.
- The whole process tree peaked at 141.5 MiB. That was the `git archive` child, not Python; capping its caches (f5f58aaf) gives
  67.5 MiB with identical bytes.
- A launch without `--source` peaks at 37 MiB, and `fetch --all` at 31 MiB.
- The same night the guardian SIGKILLed another lane's old-code launcher at 0.64 GB (16:55:48Z, vy-merge-postwave).

Real pod (vy-pod-runs-test = pujqfzfuaj15iy, cpu3c):
- Mid-ship kill: at 16:51:22Z I SIGKILLed the streaming launcher 50 MB into the ship. The pod removed the partial itself,
  leaving no READY.json and nothing executable. The full 229 MB ship never completed on the real pod: the uplink ran at about
  25 KB/s from 16:34 to 16:51Z, probably because the killed launcher was uploading the same tree. A complete streamed ship is
  shown only by the local tests.
- Bootstrap (16:55:44Z): `research run --on --cwd /workspace/src -- bash backends/direct/ligero/pod_bootstrap.sh` ran end to
  end in 2 min. rsync, rustup plus the release build of ligero-verify (10 s), uv with a Python 3.12 venv, and the torch/cupy
  installs all passed. Only "GPU stack" and "import smoke / GPU Merkle" failed, as expected without a GPU (BOOTSTRAP_FAILED).
- Guard, first run: busy 16:56-16:58, then REFUSED at 17:01:00 and 17:02:00 with run r20260924-165544-3013 unfetched.
  `fetch --all` at 17:03:03 wrote .fetched. At 17:04:01 it decided to terminate but got an empty key (the pipe/heredoc bug,
  fixed in 6fa6124f).
- Guard, second run (fixed code): REFUSED at 17:09:35 with only run 2 unfetched (run 1's marker stayed valid). `fetch --all`
  at 17:10:06, then at 17:10:36 the pod terminated itself with its own key. The API returns 404 for it now.
  Timeline: evidence/guard-e2e-monitor.log.

Credential: RunPod injects a pod-scoped `RUNPOD_API_KEY` into `/proc/1/environ`; it is not the account key (different sha256),
and ssh sessions do not inherit it. It can read nothing: REST GET /pods and /pods/{self} return 403, GraphQL myself is
Unauthorized. REST DELETE /pods/{self} returns 403, but GraphQL podTerminate of its own pod works. The guard tries REST, then
GraphQL, then runpodctl. The account key was never copied to the pod.

Only a GPU pod can confirm:
- pod_bootstrap.sh reaching BOOTSTRAP_OK: the nvidia-smi and compute-capability torch variant, torch CUDA matmul, cupy/nvrtc,
  GPU Merkle, and the health check.
- The guard's GPU signals on real nvidia-smi output (utilization and compute apps; tested with a fake nvidia-smi only).
- That RunPod GPU pods get the same pod-scoped key behaviour.

Coordinator, to deploy:
1. Merge lane/pod-runs. notes.py conflicts with steward are limited to one import line and the POD_PROBE ps/find lines.
2. Update the live CLI (`~/projects/verity-main-wt/cli`) to the merged tip, so launchers stream and fetch writes .fetched.
3. Add `guard = 90` (or N) to job-pod entries in machines.toml. Never add it to vy-control, vy-control-verity or
   vy-live2b-verifier-ro: an entry without `guard` never gets one.
4. Lanes must run `research fetch <run> --all` for every run, or the guard keeps refusing. `<root>/guard/state.json` lists
   what is unfetched.

Not done: an `/etc/rp_environment` key fallback (not needed on this image), and a size-scaled timeout for `fetch --all` (it is
still 900 s, now streamed).
