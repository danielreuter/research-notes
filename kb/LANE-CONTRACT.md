---
kind: contract
version: 1.3 (2026-09-24T22:20Z: §1 verity-agents is a start folder only)
owner: coordinator (edit in place; bump the version line)
---

# Lane contract

This contract wins over the rules sections (§0 and similar) of every older brief. A launch message says only: lane name,
base, pod, budget, FINAL time, goal, and what to read. Everything below applies to every lane.

## 1. Where you work
- Branch `lane/<you>` in the worktree `~/projects/verity-main-wt/<you>`. A successor takes over the predecessor's worktree,
  branch and pod instead (the launch message names them; `research notes bind` records it).
- You may START in the shared worker folder `~/projects/verity-agents`, but never edit there: all work happens in your
  lane's own worktree.
- Commit only there, after every meaningful step. The coordinator merges: never merge into `main`, never touch another
  worktree, never delete anyone's branch.
- Never edit, checkout or restore files in `~/projects/verity-main-wt/main` (the merge target) or
  `~/projects/verity-main-wt/cli` (the sparse worktree `~/.research/bin/research` runs; the coordinator moves it after each
  merge). For an old version of a file use `git show <rev>:<path> > /tmp/<you>-<name>` or a throwaway
  `git worktree add /tmp/<you>-<rev> <rev>`. (2026-09-24 05:06Z: old copies of relchain.py, ligero-verify main.rs and
  store/index.py left in main, which the CLI then ran, broke short art: ids for every lane.)
- No new `.md` files in the repo; notes live under `~/.research/notes`.

## 2. Tool
`~/.research/bin/research` is the current research CLI, usable from any directory. It replaces the long `PYTHONPATH=...`
prefix and any per-lane wrapper.

## 3. Report, checkpoints, inbox
- Report: `~/.research/notes/lanes/<you>/<YYYYMMDDTHHMMZ>-report-<you>.md`.
- `research notes checkpoint <you> open "<done, next, art: ids>"` at least every 20 minutes and after every result. The
  coordinator's watcher flags a lane STALE after 30 minutes with no sign of life (checkpoint, commit, worktree edit, pod work).
- `checkpoint` prints your INBOX: handoffs to you, or to the lane you took over, since you were last shown them. Act on each
  one, or say in your next checkpoint why not. At startup, run `research notes inbox <you>`.
- States: `open`, `blocked` (say on what), `final`.
- End a turn only after writing FINAL (§9), or while a command you started is still running and will notify you when it
  ends (a background shell, or a `research run` you are polling). Nothing else wakes you: a turn ended "to wait for
  notifications" with nothing running is the end of the lane. (2026-09-24: agkr-table stopped mid-plan at 08:33Z this way
  and its A100 idled 7 hours; sp1-formats finished its cells but never wrote FINAL.)

## 3a. Chatter budget (v1, 2026-09-24; the coordinator tunes it)
The coordinator and the human see every message you send and every background shell you start (each completion pings
them). Keep it to what someone must act on:
- Long pod work, bootstraps and builds included, goes through `research run --on <pod> --project verity ... -- CMD`:
  `--source . --cwd source` runs your committed tree (a recorded run), `--cwd /workspace/src` runs in the tree
  `research pods sync` keeps there (incremental builds). It returns right after launch; the pod runs and records the job
  whether or not you stay alive; `research fetch <run>` observes it. Do not hand-roll `nohup` over ssh: it produced at
  least six false "start failed" errors in one night.
  Poll with short foreground commands. Background a local shell only if it runs over ~2 minutes and you work on something
  else meanwhile.
- Checkpoints: one line, at most ~300 characters (done, next, `art:` ids). Every 20 minutes or per result, not more often
  than every 5 minutes.
- Handoffs to the coordinator only when you are blocked, need a decision, or a result changes another lane's plan.
  Everything else goes in checkpoints and the report.
- Final response: tip and outcome first, at most ~15 lines, plus one table if you measured cells.

## 4. Lost context
Your report and `git log lane/<you>` are the source of truth: continue from them. Uncommitted edits in your worktree are
yours, not another instance's.

## 5. Handoffs
- To reach another lane, write `~/.research/notes/lanes/<recipient>/<YYYYMMDDTHHMMZ>-handoff-from-<you>.md`. Its first heading
  is a one-line summary; that is what the recipient's inbox shows. Owner unknown: `lanes/coordinator/`.
- If the recipient is already final, write to the coordinator instead.
- The coordinator's instructions to you arrive only as handoffs; brief appendices are broadcasts.

## 6. Pods
- One pod unless the launch message says otherwise: `research pods create --name vy-<you> ...`, then
  `research pods sync <pod>` to ship your worktree and `research pods ssh <pod>` (`--print` gives a reusable ssh line).
- Set up with `backends/direct/ligero/pod_bootstrap.sh` (through `research run --on`, §3a), then `source env.sh`. Run with
  `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`.
- Pod scripts go in `lanes/<you>/evidence/pod-scripts/` and outputs under `/workspace/<you>/`, so a successor can find what ran.
- Register results as they land (§8). Four lanes died with their results only on the pod.
- Terminate the pod at FINAL unless the launch message says to keep it (`--keep-pod WHY`, §9).

## 7. Laptop
It is shared and nearly full. No torch, no dump trees, no CPU job over about a minute. If under 4 GB free:
`research data evict --target-free-gb 8`. `cargo clean` in your worktree before FINAL.
Every agent on this laptop lives in ONE Cursor process; a laptop memory spike kills all of them at once (14:20 PT
2026-09-23: four 8.6 GB red-team scripts). A guardian SIGKILLs any laptop Python over 1 GB under `projects/verity*`
(`~/.veritor/mem_guardian.log`); a pipe like `| tail` then hides the kill, so a "silent" truncation is usually this.
Red-team, fetch --all, reverify and tests over ~1 GB run on your pod.

## 8. Data
- `research data put ... --preserve` right after each result (pushes to R2 and verifies). Cite `art:<8+ hex>` in the report at once.
- `research data label` enforces the vocabulary (`research data vocab` lists it). Never write `verified=` yourself.
- Custody is `research data preserved <art|run>...` exiting 0, never hand-written SQL (`research data sql` prints the real
  schema when a column is wrong).
- Bench tables: `python -m verity_numerical.bench.summary DIR...` once it is on your base, instead of a per-lane `summ.py`.
- The tables the user sees, and what a result must satisfy to count in them: `kb/TABLES.md`. Read it before producing any
  result meant for Table 2/3 or a drill-down.

## 9. FINAL
- `research notes checkpoint <you> final "<one line>"` writes the line, then runs the finish checks: every `art:` id the
  report cites is preserved, no pod of yours is still running, the worktree is clean at the branch tip, and every handoff
  you received is named in the report. It exits 3 if something is left: fix it or say why not, then rerun.
- Then a `## FINAL` section in the report that opens with:

~~~text
tip: lane/<you> @ <sha> (base <branch>@<sha>)        merge-with: <branch@sha ...> | none
known-failures: <pre-existing failing tests> | none    pod: terminated HH:MMZ | kept (why); $<cost>
artifacts: art:... art:...
~~~

  and continues free-form.
- Deadlines are hard: at the FINAL time, write FINAL with what you have and what is left.
- A durable fact you found (a gotcha, a measured constant, a how-to) also goes into the matching `kb/` doc (§K).

## K. Knowledge base
`~/.research/notes/kb/` holds topic docs that anyone edits in place; this contract is one of them. Put a fact where the next
lane would look for it, with its source (`art:`, commit, report). Correct a stale fact instead of appending a contradiction.
Lane reports stay each lane's own history.

`~/.research/notes` is its own git repo (not the code repo). The coordinator's watcher commits a snapshot every pass, so
editing in place never loses history. Never run git there yourself. It holds text only: proof dumps, binaries, archives and
any file over 1 MB are not committed. Put those in the store (`research data put ... --preserve`) and cite the `art:` id instead.

## C. Coordinator: relaunching a dead lane
Save what the dead lane would lose, mark it superseded, and bind the successor to the same worktree, branch and pod:

~~~sh
L=<dead lane>; S=<successor>; w=<its worktree>; T=$(date -u +%H%MZ); d=~/.research/notes/lanes/$L/evidence; mkdir -p $d
git -C $w diff HEAD > $d/uncommitted-$T.patch; git -C $w status --short > $d/uncommitted-$T.status
git -C $w ls-files --others --exclude-standard -z | tar czf $d/uncommitted-$T-untracked.tgz -C $w --null -T -
g=$(git -C $w rev-parse --absolute-git-dir); [ -f $g/MERGE_HEAD ] && cp $g/MERGE_HEAD $d/uncommitted-$T.merge
research notes checkpoint $L superseded "by $S (coordinator): <why>"
research notes bind $S --branch <its branch> --worktree $w --pod <its pod> --succeeds $L
~~~

The successor's launch message: read this contract, then `research notes inbox $S` (it includes `$L`'s unread handoffs),
then `$L`'s report and `git log`. A mid-merge predecessor (`UU` in the status file) needs the merge finished first.
