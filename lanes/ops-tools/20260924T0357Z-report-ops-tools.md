---
lane: ops-tools
kind: report
created: 2026-09-24T03:57Z
status: final
---

CHECKPOINT aa01f247 (04:39Z) [final] A (d0fb21cc, 0b0768ed) and B (f9669c77, aa01f247) on lane/ops-tools @ aa01f247, pushed; B validated on a 4090 (terminated 04:35Z, ~$0.11); handoffs 0412Z (A) and 0437Z (B, merge after the device wave) in lanes/coordinator; kb/ops-tools.md + kb/pods-4090.md updated
CHECKPOINT f9669c77 (04:28Z) [open] A committed d0fb21cc+0b0768ed (handoff to coordinator 0412Z). B committed f9669c77 (bootstrap quota threads, research pods health + pod_health_ref.json, bench timing guard -> contention, summary contended/--best/slow-vs-ref; laptop tests green). Validating on 4090 vy-ops-tools chr1s1sfq2yeyf (up 04:26Z, terminate by 04:56Z): quota 13 of 128 cores -> threads 13 confirmed; bootstrap running.
CHECKPOINT 0b0768ed (04:08Z) [open] A committed 0b0768ed (notes: pods by ownership, IDLE-POD/ACCOUNT/RUNWAY, relaunch, reaper, gc-worktrees; 40 notes tests, suite 305 ok); handoff to coordinator; next: B (bootstrap quota threads, pods health, bench guard)
CHECKPOINT b761c3a9 (03:57Z) [open] started: read contract/code; building A (pods by ownership, idle/account/runway alerts, relaunch, gc-worktrees) in notes.py; next: tests + commit A by 05:00Z

## FINAL

~~~text
tip: lane/ops-tools @ aa01f247 (base main@b761c3a9)        merge-with: none
known-failures: backends/numerical/tests/bench/test_tables.py::test_label_keys_are_the_store_vocabulary (fails on main b761c3a9 too)    pod: terminated 04:35Z; $0.11
artifacts: none (tool validation, not campaign results: lanes/ops-tools/evidence/b-validation-4090/)
~~~

Part A (d0fb21cc, 0b0768ed; merge now; handoff 20260924T0412Z-handoff-from-ops-tools.md), in `notes.py` with 40 notes tests:
* Pods belong to lanes by ownership: a lane owns every `vy-<topic>[<letter>][-<role>]` pod for any attempt in its succession
  chain, and `bind --pod` is only a hint. `status` shows each pod with its $/h, busy/serve/idle state and GPU util.
* One row per topic (`#N` = attempt); `--all` also shows predecessors.
* `watch` alerts: IDLE-POD (an open lane's pod idle >= `--idle-min`), ACCOUNT (every pass), RUNWAY (< `--runway-h`), FINAL-POD.
  With `--reap`: REAPED plus `reaper.log`, sparing pods kept by `--keep-pod`. MAIL is not printed on the first pass or for
  superseded lanes.
* `relaunch` does contract §C in one command. `bind` takes `--brief/--final/--budget`. `gc-worktrees [--apply]` removes clean,
  pushed worktrees of done lanes.

Part B (f9669c77, aa01f247; merge after the device wave; handoff 20260924T0437Z-handoff-from-ops-tools.md), validated on a 4090:
* B1: `pod_bootstrap.sh` sets `OMP/MKL/OPENBLAS_NUM_THREADS = VY_CPU_THREADS = floor(cgroup quota)` in env.sh and caps NP at
  the quota. Tested against the v1 and v2 cgroup layouts. On the pod: 13 of 128 cores, and torch's intra-op pool was 13.
* B2: `research pods health <pod>` (also run at the end of bootstrap) reports quota vs nproc, GPU clocks, power, PCIe and
  persistence under load, other GPU processes and disk. Its ~20 s benchmark (encode + matmul) is compared with
  `pod_health_ref.json`; DEGRADED exits 3. On the pod: OK at 1.00x, and DEGRADED at 7.6x encode / 2.2x matmul beside a GPU hog.
  Only rtx-4090 has a reference entry so far.
* B3: a timing guard on `run.py bench` / `bench-vu` writes `contention` into the result, and bench_result carries it into
  result.json. It flags other GPU processes, throttling while the GPU is busy, and host load above the core count. On the pod:
  clean 0.0301 s; beside a hog 0.0619 s (contended); at host load 148 on 128 cores 0.0331 s (contended). `summary` shows
  `contended`, and `--best` refuses contended rows.
* B4: `summary` adds `vs_ref` / `ref` / `flag slow-vs-ref` (more than 15 % slower), compared with the fastest preserved store
  result of the same relation, gpu, auth, l, pipe, VUs, zk and mode. A reference must name its GPU.

Left:
* Table 2 selection (`tables.reject_reasons`, frozen, not mine) does not refuse contended results yet. The one-line proposal is
  in the 0437Z handoff.
* Health references for SKUs other than the 4090 still need recording (`research pods health <pod> --record` on a known-good
  pod, then commit the file).
* torch's inter-op pool still sizes itself to nproc.
