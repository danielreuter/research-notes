---
campaign: robustness
created: 2026-09-24T16:15Z
owner: coordinator
---

# Robustness, step 1: duties that do not depend on an agent being awake

User-approved 2026-09-24 ~16:05Z (proposal in the coordinator chat; summary here). Principle: agents are disposable, state
and duties are not. Whatever must happen (pods terminated, tables rendered, dead lanes woken, results verified) gets an
owner that is not an agent; agents do judgment and can always be woken or replaced from files.

Evidence (night of 2026-09-23/24): the coordinator's Cursor host restarted at 06:51Z (3.3 GB) and no event reached it
until 15:39Z; the watcher flagged every problem within ~15 min but may only report; agkr-table ended its turn mid-plan at
08:33Z and its A100 idled 7 h (~$11) because the reaper only reaps FINAL lanes; sp1-formats finished but never wrote FINAL;
the guardian killed `research run --on` launchers 4x during the source ship (0.55-0.69 GB each); lanes hand-rolled
`nohup` over ssh and got at least six false "start failed" errors; `pods/sh/pod_guard.sh` (pod self-termination,
2026-09-13) exists but was never wired into this campaign.

Steps: (1) steward rules + pod-side guard + CLI worktree [this brief]; (2) lanes launched through the Cursor SDK so the
steward can wake or relaunch them (DEFERRED 16:25Z: the user will pilot Cursor himself later); (3) validity check at
`research data put` + auto verification queue (the contract.result lane); (4) steward and agents off the laptop.

Done by the coordinator (16:00Z): `~/.research/bin/research` now runs `~/projects/verity-main-wt/cli`, a sparse detached
worktree at main (tools/research + backends/numerical) that only the coordinator moves after merges; the watcher
(`launchctl` label com.research.notes-watch, runs the shim) was restarted on it. LANE-CONTRACT §1/§3/§3a/§6 updated
(turn-ending rule; long pod work through `research run --on`).

| lane | base | worktree (sparse) | pod | budget | FINAL |
|---|---|---|---|---|---|
| steward | main 0b0768ed | ~/projects/verity-main-wt/steward (tools/research, backends/numerical) | none | $0 | 18:30Z |
| pod-runs | main 0b0768ed | ~/projects/verity-main-wt/pod-runs (tools/research, backends/direct/ligero) | one throwaway CPU pod | $2 | 18:30Z |

Tests (either lane): `cd /tmp && PYTHONPATH=<worktree>/tools/research/src ~/projects/verity-main-wt/main/.venv/bin/python -m
pytest -q -p no:cacheprovider <worktree>/tools/research/tests/...`. Laptop limits (LANE-CONTRACT §7) apply: ~6 GB free disk,
the guardian kills big processes.

## steward: the watcher acts on mechanical rules (tools/research/src/research/notes.py)

All inside `research notes watch`; every destructive call injectable and unit-tested with fakes (like `reap_lines`).
1. Stale-lane pods (with `--reap`): a lane that is STALE (not final, not superseded, no keep_pod) whose pod has been idle
   (the existing probe: GPU 0 %, no work process) for >= `--reap-stale-min` (default 30) is terminated only if custody
   passes: (a) every `art:` id its newest report cites is PRESERVED on the remote (the same check as
   `research data preserved`), and (b) every local run whose remote machine is that pod has preserved.json or a
   registered artifact. Else `REAP-BLOCKED <lane> <pod>: <first reason>` once per pod per 30 min. Log to reaper.log.
   The watcher's environment has no R2 credentials: load `~/.config/verity/r2.env` (KEY=VALUE lines) when the vars are unset.
2. Deadline: binding `final` HH:MMZ; `OVERDUE <lane>` once when now > final + 30 min and the lane is not final.
3. Budget: accumulate each lane's pod $ per pass (usd/h x elapsed) in `<root>/steward-state.json`; `OVER-BUDGET <lane>`
   once when above the binding's budget (first `$<number>`). Alert only.
4. Scheduled render: `<root>/steward.toml`, re-read every pass:
   ~~~toml
   [[render]]
   at = "12:30Z"                                   # daily, UTC; once per UTC day per entry (state file)
   source = "~/projects/verity-main-wt/cli"        # has backends/numerical and tools/research
   out = "campaigns/morning-tables/render"         # relative to the notes root
   store = "~/.research/store"
   ~~~
   Run `python -m verity_numerical.bench.tables --root STORE --format md` and `python -m verity_numerical.bench.drilldown
   --root STORE --format md` with PYTHONPATH=source/backends/numerical/python:source/tools/research/src:source, write
   `<out>/<YYYYMMDDTHHMMZ>-tables.md` / `-drilldowns.md`, print `RENDERED <path>`; failure or 10 min timeout:
   `RENDER-FAILED <entry>: <stderr tail>`. The existing snapshot commits the files.
5. Guardian kills to the owning lane's inbox: tail `~/.veritor/mem_guardian.log` from a saved offset; map each `KILLED`
   line to a lane by `--on <machine>` in its cmd (machines.toml -> pod -> pod_owner) or by the process cwd lying under a
   bound worktree; write one handoff per lane per pass, `lanes/<lane>/<stamp>-handoff-steward-guardian.md` (front matter
   lane / kind: handoff / from: steward / created; first heading = one-line summary; body = the kill lines and "killed on
   the laptop by the guardian, not on the pod: rerun it"), print `ROUTED <lane> <n>`; unmapped: `KILLED-UNOWNED <line>`.
   The guardian must log the cwd for the second rule: write the change to `~/.veritor/mem_guardian.py` as a patch in
   `lanes/steward/evidence/` (the coordinator applies it; the guardian is a live launchd service; do not edit it in place).
6. Update the notes.py docstring's alert list. Do not restart the watcher; the coordinator deploys after merge.

## pod-runs: detached pod work that also cleans up after itself

1. `research run --on --source`: measure the laptop RSS of a launch of this repo, then stream the source archive
   (`git archive` -> sha256 -> ssh) so the launcher stays under ~150 MB whatever the tree size. Keep every guarantee of
   remote.py's docstring (digest and manifest compare, READY.json, SourceNotReady, no half tree ever executes).
2. Pod-side guard, started by the machine side of `research run --on` (launch-request), one per pod (pidfile), built
   from `pods/sh/pod_guard.sh` rather than a rewrite:
   - idle: no live research runner, no work process (share the definition the watcher's pod probe uses in notes.py),
     GPU utilisation 0, for IDLE_MIN (default 90) minutes -> the pod terminates itself;
   - durability: refuse while any run dir under <root>/runs has not been fetched with `research fetch --all` (make fetch
     --all write `<run>/.fetched` on the pod once every file verified); re-check every loop; log the refusing run ids;
   - credential: terminate with the pod's own RunPod-injected key if the pod has one (check /proc/1/environ; verify on a
     real pod that it can terminate itself). If no pod-scoped key exists, do not install the guard and say so in the launch
     output. Never copy the account key (~/.runpod/config.toml) to a job pod;
   - state: <root>/guard/state.json (last activity, idle minutes, refusal reasons) for the laptop probe.
3. On one throwaway CPU pod (cpu3c, <= $2 total, terminated at FINAL): streaming-ship RSS before/after; killing the
   launcher mid-ship leaves nothing executable; guard with IDLE_MIN=3 refuses while a run is unfetched and terminates the
   pod after `research fetch --all`; the credential check. Whether `pod_bootstrap.sh` runs cleanly through
   `research run --on <pod> --cwd /workspace/src` is the LANE-CONTRACT's new rule: check what you can on CPU and say what
   only a GPU pod can confirm.
