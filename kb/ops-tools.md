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

## Catalog wipes and rendering on a pod (verify-night, 2026-09-24)
* `research data reindex` (`Index.rebuild`) empties the catalog tables first and refills them in stages, so an interrupted
  reindex leaves a catalog with few artifacts and 0 attempts/labels. Table 2 then renders silently wrong, and `research data
  evict` finds nothing to evict. Two causes were seen: a concurrent `research data preserved` holding the SQLite lock, and the
  guardian killing reindex once laptop free disk falls under its 3.5 GB floor (`~/.veritor/mem_guardian.log`).
* To render when the laptop can't reindex, copy the laptop's `manifests/ attempts/ labels/` to the pod store. Run
  `COPYFILE_DISABLE=1 tar`, or delete macOS `._*` files on the pod afterwards, because they double the counts. Then run
  `research data labels-sync --pull-only` and `reindex --remote` there, which fetches only what the pod lacks (about 5 min).
  Script: `lanes/verify-night/evidence/pod-scripts/21-pod-render.sh`.
* `reverify.py` on runner-attempt results reads `attempts/`. A `mint-credential` scoped to objects/manifests/labels fails with
  HTTP 403, so add `--prefix attempts/`.
