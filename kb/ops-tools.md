# Ops tools: watching lanes, relaunching, pod health, contended timings

Lane ops-tools, 2026-09-24. Code: `tools/research/src/research/notes.py` (watch, status, relaunch, gc-worktrees),
`tools/research/src/research/pods/health.py`, `backends/direct/ligero/{pod_bootstrap.sh,pod_health.py,timing_guard.py}`,
`verity_numerical.bench.summary`. Part A is commits d0fb21cc and 0b0768ed; part B is on `lane/ops-tools` (merge it after the device wave).

## Watching lanes (coordinator)
~~~sh
research notes watch --every 2 --stale-min 12 --idle-min 5 --runway-h 3 --pods --snapshot   # minutes; add --reap once trusted
~~~
* `IDLE-POD <lane> <pod> <N>m`: an open lane's pod has shown 0 % GPU and no busy process for N minutes. This is the earliest
  sign that the lane died. Printed once for each idle spell.
* `ACCOUNT`: balance, account $/h, runway in hours, and $/h of lane-owned pods vs other pods. `RUNWAY <h>h` fires below `--runway-h`.
* `FINAL-POD`: a final lane (with no open successor) still owns a pod. With `--reap`, the pod is terminated after 10 minutes
  (`REAPED`, logged to `~/.research/notes/reaper.log`) unless the lane recorded `--keep-pod WHY`. A pod no lane owns is never touched.
* Steward rules (`lane/steward` @ e7d4a978, live once merged and the watcher restarted; lanes/steward report `## FINAL`).
  Their memory is `<root>/steward-state.json`, which the snapshot leaves out:
  * `REAPED` / `REAP-BLOCKED <lane> <pod>: <reason>`: with `--pods --reap`, a STALE lane's pod idle for `--reap-stale-min` (30)
    is terminated only after custody passes. Custody means every `art:` its newest report cites is preserved on R2, and every
    run on the pod has preserved.json or a store attempt. A blocked pod is re-checked every 30 min. Both lines go to reaper.log.
  * `OVERDUE <lane>`: not final 30 min after the binding's `final`. `OVER-BUDGET <lane>`: the lane's pod $ passed the
    binding's first `$<n>`. Each fires once; both are alerts only.
  * `RENDERED <path>` / `RENDER-FAILED <entry>: <why>`: `[[render]]` entries of `<root>/steward.toml` (`at`, `source`, `out`,
    `store`), daily. `bench.tables` on the real store took 2.4 s and 83 MB on 2026-09-24. `bench.drilldown` is not on main yet.
  * `ROUTED <lane> <n>` / `KILLED-UNOWNED <line>`: guardian kills become a handoff in the owning lane's inbox, or the
    coordinator's when that lane is final. The owner comes from `--on <machine>`, or from the cwd, which needs the guardian
    patch `lanes/steward/evidence/mem_guardian-cwd.patch`.
  * `STEWARD-ERROR <rule>: <error>`: a rule raised; the watch goes on.
* `status`: one row per topic (the latest attempt, `#N`). Each pod the lane owns (`vy-<topic>[<letter>][-<role>]`, any attempt of
  the succession) shows its $/h, busy/serve/idle state and GPU util. `--all` also shows the predecessors.
* MAIL is never printed on the first pass, and never for a superseded lane (its successor's inbox carries the mail).

## Relaunching a dead lane
~~~sh
research notes relaunch <lane> [--as <successor>]    # contract §C in one command; prints the launch message to paste
research notes gc-worktrees [--apply]                # lists, then removes, clean + pushed worktrees of final / superseded lanes
~~~
`relaunch` saves uncommitted work to `lanes/<lane>/evidence/uncommitted-<HHMMZ>*`, checkpoints `<lane> superseded`, and binds
`<topic>-<N+1>` to the same branch, worktree and pods. `bind --brief/--final/--budget` values carry into the launch message.

## Pods
* `pod_bootstrap.sh` sizes the thread pools to the cgroup CPU quota. env.sh sets `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS` and `VY_CPU_THREADS` to floor(quota). torch's intra-op pool follows (checked: 13 on a 13.6-core 4090 pod);
  its inter-op pool does not (still nproc). GNU `nproc` honours `OMP_NUM_THREADS` too, so `$(nproc)` in scripts gives the quota
  after `source env.sh`. The instance-build `NP` is capped at the quota. The bootstrap ends with the health check (`HEALTH=0` skips it).
* `research run --on` does NOT source env.sh, so a recorded workload script has to export the four caps itself (floor of
  `cpu.cfs_quota_us / cpu.cfs_period_us`). Without them, a 5090 pod (13.6-core quota, nproc 32) measured the A-GKR fp4-nvf4
  prover at 0.314 s instead of 0.274 s, and the Rust verifier at 0.19 s instead of 0.164 s. Same tree, same proof bytes; it
  reproduced by hand outside research run. See lane agkr-nvf4, `04_record.sh`.
* `research pods health <pod>` reports quota vs nproc, GPU clocks, power limit, PCIe gen/width and persistence (read under load),
  other GPU processes and free disk. It then runs a ~20 s benchmark (SIMT encoder at l=4096 x 2048 rows, and a bf16 8192^3 matmul)
  against the SKU's entry in `backends/direct/ligero/pod_health_ref.json`. `DEGRADED` (exit 3) means replace the pod.
  `--record` folds this pod into the reference (per metric, the best pod seen); commit the file afterwards.
  rtx-4090 reference: 0.330 ms encode, 160.4 TFLOP/s (vy-ops-tools, US-TX-3, 2026-09-24). Other SKUs have no entry yet:
  run `--record` on a known-good pod.
* Timing guard: every `run.py bench` / `bench-vu` writes a `contention` record into its `--out` result, and bench_result.py
  carries it into result.json. The run is marked contended when it saw other GPU compute processes, CPU throttling in more than
  10 % of cgroup periods while the GPU was busy, or a host load above the core count. `VY_TIMING_GUARD=0` turns the guard off.
* `python -m verity_numerical.bench.summary ...` shows a `contended` column. `--best` keeps the fastest non-contended, non-failed
  row per config and names each refused row. `vs_ref` / `ref` / `flag slow-vs-ref` (more than 15 % slower) compare a row with
  the fastest preserved (R2) store result of the same relation, gpu, auth, l, pipe, VUs, zk and mode. `--no-refs` skips the lookup.
* `research run --on ... -- CMD` runs CMD as an argv, with no shell: `-- bash '$RESEARCH_RUN_DIR/inputs/x.sh'` fails with rc 127
  ("No such file or directory"). Without `--cwd` the run dir is the cwd, so use `-- bash inputs/x.sh`. With `--cwd`, use
  `-- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/x.sh"'` (merge-postwave, r20260924-170644-a490).
* A pod job started as `ssh pod 'nohup cmd &'` can die with an empty log, for example when the same ssh call also had stdin
  piped in. `ssh pod '(setsid nohup cmd > log 2>&1 < /dev/null &)'` survives the session. `research pods drain <pod>` is the
  clean way to terminate at FINAL: it lists the attempts and refuses while any is unpreserved (agkr-nvf4, 2026-09-25).
* The runpod CPU image (Ubuntu 22.04) has curl. Listing `curl` in `apt-get install` made apt upgrade it from a security-pool URL
  that returned 404, and the whole install failed with rc 100. Leave curl and ca-certificates out of the list (merge-postwave, 2026-09-24).

## Pod guard and streamed ships in `research run --on` (pod-runs, 2026-09-24, lane/pod-runs)
* Opt a job pod in with `guard = N` (idle minutes; `true` = 90) in its `machines.toml` entry. An entry without `guard` never
  gets one, so a control pod or live verifier stays untouched. The launch prints `guard on pod ...: pid P (started | already
  running)` or `NO guard on <machine>: <reason>`. One daemon per pod (`<root>/guard/guard.pid`), started by `launch-request`.
* It terminates the pod after N minutes with no live runner, no work process, no live verifier and 0 % GPU. The definition is
  `research/pods/workproc.py`, which the watcher's pod probe uses too. It refuses, and re-checks every minute, while any
  `<root>/runs/*` lacks a valid `.fetched`. `research fetch <run> --all` writes that marker on the pod after verifying every
  file. A file changed after the verification makes the run unfetched again. State for the laptop: `<root>/guard/state.json`
  (verdict, idle_min, last activity, unfetched runs with reasons, terminate attempt). Log: `<root>/guard/guard.log`.
* Pod credential (measured on a cpu3c pod): RunPod puts a pod-scoped `RUNPOD_API_KEY` (not the account key) in `/proc/1/environ`.
  ssh sessions do not inherit it. It can read nothing: REST `GET /pods` and `/pods/{self}` return 403, and GraphQL `myself` is
  Unauthorized. REST `DELETE /pods/{self}` returns 403 too, but GraphQL `podTerminate` of its own pod works, and the guard used
  it (17:10:36Z). The account key never goes to a job pod. The one exception is the shared control pod `vy-control-verity`: its
  `/root/.runpod/config.toml` holds an account key, which the `vyv-` budget, deadline and balance-floor daemons use to list and
  terminate pods (vllm-coordinator, 2026-09-24).
* Gap: `research run` doesn't pull a run's store inputs onto the pod. The regression gate's fixture trees need an R2 credential on
  the pod. Interim, owner-approved route: a lane mints its own read-only key on the laptop (`--ttl 3h`; never on a pod, which
  would need the R2 admin key), pipes it into its own pod, fetches, and deletes the key at once. The recipe is the gate (a) block
  in `lanes/vllm-rf-a1/baseline.md`. The fix: the launcher fetches declared inputs onto the pod itself.
* When the laptop -> pod link can't ship a source tree within `ship_timeout`, copy it from a pod that has it. Put an ephemeral
  ed25519 key on the source pod and add its `.pub` to the target's `authorized_keys`. Tar `<root>/src/<sha>/` without `READY.json`
  or bootstrap outputs (e.g. `integrations/vllm/out/`) into a staging dir, then `mv -T` it into place and delete the key on both
  pods. The next `research run --source` sees a legacy tree and adopts it after a per-file sha256 check against its own git
  manifest (`verified: legacy-sha256-per-file`). g1b -> tp2 ran at 2.9 MiB/s where the laptop link timed out twice
  (vllm-coordinator for vllm-rf-f1, 2026-09-24).
* To stop a guard on your own pod, run `pkill -f "[p]od_guard.sh daemon"`. Without the brackets, pkill also kills the ssh shell
  running it.
* The launcher streams the source archive. Its Python stays around 20 MiB during the ship and peaks near 40 MiB (the manifest
  pass). `git archive` peaks near 70 MiB with the cache caps in remote.py. The old code peaked at 611 MiB, and one such launcher
  was SIGKILLed at 0.64 GB at 16:55Z. The laptop's uplink fell to about 25 KB/s at 16:34-16:51Z (likely a concurrent upload of
  the same 229 MB tree) and was fast again right after. A full `--source` ship can take over an hour at that rate; the timeout is
  archive size / 64 KiB/s.

## Catalog wipes and rendering on a pod (verify-night, 2026-09-24)
* `research data reindex` (`Index.rebuild`) empties the catalog tables first and refills them in stages, so an interrupted
  reindex leaves a catalog with few artifacts and 0 attempts/labels. Table 2 then renders silently wrong, and `research data
  evict` finds nothing to evict. Two causes were seen: a concurrent `research data preserved` holding the SQLite lock, and the
  guardian killing reindex once laptop free disk falls under its 3.5 GB floor (`~/.veritor/mem_guardian.log`).
* To render when the laptop can't reindex, copy the laptop's `manifests/ attempts/ labels/` to the pod store. Run
  `COPYFILE_DISABLE=1 tar`, or delete macOS `._*` files on the pod afterwards, because they double the counts. Then run
  `research data labels-sync --pull-only` and `reindex --remote` there, which fetches only what the pod lacks (about 5 min).
  Script: `lanes/verify-night/evidence/pod-scripts/21-pod-render.sh`.
* On a fresh pod with an empty catalog, `reindex --remote` fetches manifests one by one (~150/min, over an hour for the
  full store; verify-po 2026-09-24). A verifier doesn't need it: pass FULL art ids, since `get_manifest`, `get_attempt`
  and `fetch` fall back to the remote (`lanes/verify-po/evidence/pod-scripts/03-reverify.sh`).
* `reverify.py` on runner-attempt results reads `attempts/`. A `mint-credential` scoped to objects/manifests/labels fails with
  HTTP 403, so add `--prefix attempts/`.
* Laptop render from a lane worktree whose `.venv` is empty: the shell's PYTHONPATH points at the `cli` worktree, so
  `uv run ... bench.tables` fails with "No module named verity". Instead, run main's interpreter read-only from /tmp:
  `env -u PYTHONPATH ~/projects/verity-main-wt/main/.venv/bin/python -m verity_numerical.bench.tables --format json`
  (2 s; verify-po 2026-09-25).

## tools/research tests in a sparse worktree (steward, 2026-09-24)
* In a worktree sparse on `tools/research` + `backends/numerical`, 12 tests of the tools/research suite fail already at base
  0b0768ed: `test_pythonpath.py` (2), `test_store_prov.py` (3) and `test_store_vllm_tools.py` (7). They load `integrations/vllm`,
  `tools/tc_probe`, `backends/direct/ligero` and `backends/sp1`. The counts are 304 passed, 12 failed, 4 skipped there, against
  319 passed, 1 skipped in a full tree. Cite them as known-failures.
* A full temporary tree costs about 225 MB, so make one only with disk to spare and remove it right after. `git worktree add`
  copies the sparse-checkout config of the worktree it runs from, so run `git sparse-checkout disable` in the new tree.
