---
lane: steward
kind: report
created: 2026-09-24T16:11Z
status: final
---

CHECKPOINT e7d4a978 (16:33Z) [final] 5 steward rules in notes watch @ e7d4a978 (REAPED/REAP-BLOCKED, OVERDUE, OVER-BUDGET, RENDERED/RENDER-FAILED, ROUTED/KILLED-UNOWNED); test_notes 51 pass, full suite 319 pass in a full tree; guardian cwd patch + deploy steps in report FINAL
CHECKPOINT c61feb9e (16:25Z) [open] all five rules implemented + tested (51 notes tests); temp-root e2e drives main() twice through all five rules (evidence/e2e-output.txt); full suite in a full temp worktree running; FINAL next
CHECKPOINT fc27f1e1 (16:19Z) [open] 5 rules implemented in notes.py + 10 tests (50/50 test_notes pass) @ fc27f1e1; next: guardian cwd patch, temp-root e2e with fake pods, full suite
CHECKPOINT 0b0768ed (16:11Z) [open] read contract, brief, notes.py, drain.py, preserved.py, guardian; design done for the 5 rules; next: implement in notes.py + tests, guardian cwd patch

## FINAL

~~~text
tip: lane/steward @ e7d4a978 (base main@0b0768ed)        merge-with: none
known-failures: none in a full tree; in this sparse worktree 12 fail at base too (kb/ops-tools.md)    pod: none; $0
artifacts: none
~~~

`research notes watch` now acts on the five rules of the brief. The code is in `notes.py` and the tests in `test_notes.py`
(40 -> 51 tests); every destructive call (terminate, lane-dir writes) is injected and faked in the tests. Output lines:

1. Stale-lane pods, with `--pods --reap`. Success prints `REAPED <lane> <pod> <id> $x/h (STALE Nm, idle Nm); custody: ...`.
   Otherwise `REAP-BLOCKED <lane> <pod>: <first reason>`, re-checked every 30 min. Both go to reaper.log.
   - Custody (a): `preserved.check` on each cited `art:`. A verified remote replica already recorded counts; otherwise the
     head check runs, provided the blobs it must read back come to 64 MB or less.
   - Custody (b): every local run whose remote.json names the pod has preserved.json or a store attempt. An attempt is written
     only after its outputs are registered.
   - R2 credentials come from ~/.config/verity/r2.env when unset.
2. `OVERDUE <lane> FINAL HH:MMZ passed Nm ago: ...`, once, 30 min after the binding's `final`. The deadline is the first such
   HH:MMZ after the binding was written. Final lanes never get it.
3. `OVER-BUDGET <lane> $x on pods > $y (budget: ...); now $z/h`, once. Spend accumulates per pass in `<root>/steward-state.json`,
   which the snapshot leaves out.
4. `RENDERED <path>`, or `RENDER-FAILED <out>@<at> (tables|drilldown): <stderr tail>`. Entries come from `<root>/steward.toml` and
   run once per UTC day at or after `at`, with a 10 min cap. A check through `watch` on a temp root against the real store
   rendered tables in 2.4 s using 83 MB. Drilldown fails until `verity_numerical.bench.drilldown` exists on the source tree.
5. `ROUTED <lane> <n>: <handoff>`, or `KILLED-UNOWNED <line>`. A final lane's kills go to the coordinator instead (contract §5):
   `ROUTED coordinator <n>: ... (<lane> is final)`. The guardian patch logs the killed process's cwd, read with lsof before the
   kill: evidence/mem_guardian-cwd.patch.

A rule that raises prints `STEWARD-ERROR <rule>: <error>`, and the watch goes on.

Evidence: evidence/e2e_steward.py runs the real `main()` twice on a temp root; the second run is a restart. The RunPod API is
faked at its lowest level (pod list, balance, DELETE). The store is real, with an fs remote; the runs, guardian log and render
source are fakes. Its output, evidence/e2e-output.txt, shows every line above. The only DELETE calls hit the two intended pods,
and steward-state.json stays untracked.

Tests: test_notes.py 51 passed. The whole tools/research suite in a full tree at e7d4a978: 319 passed, 1 skipped (110 MB peak).

Handoffs received: 20260924T1628Z-handoff-coordinator-fulltree.md. I removed /tmp/steward-fulltree at 16:31Z, after its suite
run had finished.

Deploy (coordinator):

~~~sh
git -C ~/projects/verity-main-wt/main merge --no-ff lane/steward
git -C ~/projects/verity-main-wt/cli checkout --detach main      # the tree ~/.research/bin/research runs (detached at 0b0768ed)
cp ~/.veritor/mem_guardian.py ~/.veritor/mem_guardian.py.bak
patch ~/.veritor/mem_guardian.py < ~/.research/notes/lanes/steward/evidence/mem_guardian-cwd.patch   # dry-run clean at 16:33Z
/usr/bin/python3 -m py_compile ~/.veritor/mem_guardian.py && launchctl kickstart -k gui/$(id -u)/com.veritor.memguardian
cat > ~/.research/notes/steward.toml <<'EOF'
[[render]]
at = "12:30Z"
source = "~/projects/verity-main-wt/cli"
out = "campaigns/morning-tables/render"
store = "~/.research/store"
EOF
launchctl kickstart -k gui/$(id -u)/com.research.notes-watch
~~~

The submitted watcher job already runs with `--pods --reap`, which rules 1 and 3 need. `--reap-stale-min 30` and
`--guardian-log ~/.veritor/mem_guardian.log` are the defaults, so the job needs no new flags.

What to expect after the restart:
- With the live `--stale-min 12`, rule 1 terminates a pod once its lane has been silent 12 min, the pod has been idle 30 min,
  and custody passes. Raise `--reap-stale-min` if lanes legitimately leave pods idle.
- The first pass may alert OVERDUE and OVER-BUDGET for lanes already past their deadline or budget. Spend counts from each
  pod's start; pods terminated before the deploy are not counted.
- The guardian log's first look only records where it ends, so old kills are not routed.
