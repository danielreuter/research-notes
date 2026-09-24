---
kind: contract
version: 1.2 (2026-09-24T03:55Z: §3a chatter budget)
owner: coordinator (edit in place; bump the version line)
---

# Lane contract

This contract wins over the rules sections (§0 and similar) of every older brief. A launch message says only: lane name,
base, pod, budget, FINAL time, goal, and what to read. Everything below applies to every lane.

## 1. Where you work
- Branch `lane/<you>` in the worktree `~/projects/verity-main-wt/<you>`. A successor takes over the predecessor's worktree,
  branch and pod instead (the launch message names them; `research notes bind` records it).
- Commit only there, after every meaningful step. The coordinator merges: never merge into `main`, never touch another
  worktree, never delete anyone's branch.
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

## 3a. Chatter budget (v1, 2026-09-24; the coordinator tunes it)
The coordinator and the human see every message you send and every background shell you start (each completion pings
them). Keep it to what someone must act on:
- Long jobs run detached on the pod (`nohup ... > /workspace/<you>/x.out 2>&1 &` over ssh); poll with short foreground
  commands. Background a local shell only if it runs over ~2 minutes and you work on something else meanwhile.
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
- Set up with `backends/direct/ligero/pod_bootstrap.sh`, then `source env.sh`. Run with `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`.
- Pod scripts go in `lanes/<you>/evidence/pod-scripts/` and outputs under `/workspace/<you>/`, so a successor can find what ran.
- Register results as they land (§8). Four lanes died with their results only on the pod.
- Terminate the pod at FINAL unless the launch message says to keep it (`--keep-pod WHY`, §9).

## 7. Laptop
It is shared and nearly full. No torch, no dump trees, no CPU job over about a minute. If under 4 GB free:
`research data evict --target-free-gb 8`. `cargo clean` in your worktree before FINAL.

## 8. Data
- `research data put ... --preserve` right after each result (pushes to R2 and verifies). Cite `art:<8+ hex>` in the report at once.
- `research data label` enforces the vocabulary (`research data vocab` lists it). Never write `verified=` yourself.
- Custody is `research data preserved <art|run>...` exiting 0, never hand-written SQL (`research data sql` prints the real
  schema when a column is wrong).
- Bench tables: `python -m verity_numerical.bench.summary DIR...` once it is on your base, instead of a per-lane `summ.py`.

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
