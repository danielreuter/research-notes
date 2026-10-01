---
cursor:
  subagentId: "bc-4100fff0-95e2-5fbf-a7dd-2bcabac71388"
---

# Cloud lane setup: read this before your lane brief

You are a research lane running as a Cursor cloud agent in `danielreuter/verity`. The laptop worker is for coordinators
only (Daniel's rule). This page adapts `LANE-CONTRACT.md` to a cloud VM. Where it conflicts with the contract, this page
wins. Notes push directly with the `RESEARCH_NOTES_TOKEN` secret, and the store mirror is the fallback (section 1).

## 1. Environment, once per shell

Notes go **direct** (your own research-notes clone, pushed with the `RESEARCH_NOTES_TOKEN` secret) when the token is set
and the clone works. Otherwise they go through the **store mirror** fallback. Paste this block into every new shell. It
never prints the token: the token stays in the environment, and git reads it through a credential helper.

```bash
export STORE=/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d
export RESEARCH_WRITE_THROUGH=1                # artifacts, attempts and labels go to R2 as they're written
export NOTES_CLONE=$HOME/research-notes
# The username in the URL matters. The VM's global ~/.gitconfig rewrites https://github.com/ to the Cursor App token,
# which gets a 403 on research-notes. https://notes@github.com/ doesn't match that rule, so git asks the helper.
NOTES_URL=https://notes@github.com/danielreuter/research-notes.git
NOTES_HELPER='!f() { test "$1" = get && echo "password=$RESEARCH_NOTES_TOKEN"; }; f'
if [ -n "$RESEARCH_NOTES_TOKEN" ] && { [ -d "$NOTES_CLONE/.git" ] || \
     git -c credential.helper= -c "credential.helper=$NOTES_HELPER" clone -q "$NOTES_URL" "$NOTES_CLONE"; }; then
  git -C "$NOTES_CLONE" remote set-url origin "$NOTES_URL"
  git -C "$NOTES_CLONE" config --replace-all credential.helper ''    # drop inherited helpers
  git -C "$NOTES_CLONE" config --add credential.helper "$NOTES_HELPER"
  git -C "$NOTES_CLONE" pull -q --rebase --autostash origin main
  export RESEARCH_NOTES=$NOTES_CLONE RESEARCH_MACHINES_D=$NOTES_CLONE/machines.d
  export RESEARCH_NOTES_SYNC=1                 # checkpoint / bind / relaunch / pods --register push on success
  echo "notes: direct ($NOTES_CLONE)"
else
  export RESEARCH_NOTES=$STORE/internal        # fallback: the store mirror of kb/, lanes/<lane>/, machines.d/
  export RESEARCH_MACHINES_D=$STORE/internal/machines.d
  unset RESEARCH_NOTES_SYNC
  echo "notes: store mirror (fallback)"
fi
```

- **Direct mode:** `research notes checkpoint <lane> ...` commits your lane directory and pushes it at once (fetch,
  rebase, bounded retries; it refuses a push that contains key material). `research notes sync --path lanes/<lane>`
  pushes anything else you wrote in the notes. Check the last line of each command's
  output: `notes sync: committed <sha> (...); pushed`. If you see `FAILED`, the local commit is kept. Fix the cause and
  run `research notes sync` again. `403 ... denied to cursor[bot]` means the remote URL lost its `notes@` and the global
  rewrite took over, so re-run the block. Never paste the token into a URL, argv or file.
- **Fallback mode** (no token, or the clone fails): sections 2 and 4 work as written. You write plain files in the store,
  and the coordinator mirrors and publishes them.
- Verified 2026-09-25 17:24Z (10:24 PT) from a cloud VM: helper clone, then `research notes sync` push and delete on
  `main`.
- The CLI is the repo's `research` entry point (`tools/research`, `research = "research.cli:main"`). From the repo root,
  use whichever works in your environment: `research ...`, `uv run research ...`, or
  `PYTHONPATH=tools/research/src python3 -m research ...`. Check that `research notes inbox <lane>` answers.
- Credentials come from the cloud environment: `RUNPOD_API_KEY`, `RUNPOD_SSH_KEY_B64`, `R2_*`, `AWS_*`,
  `RESEARCH_NOTES_TOKEN`. The CLI and git read them directly. Never print them, never put them in argv, and **never copy
  them to a pod**. Pods get only what `research run` gives them.
- **To see which variables are set, list names only:** `compgen -e`, or `compgen -e | rg NAME`. Never use `env`, `printenv`,
  `set`, or `env | cut -d= -f1`. Multi-line values such as `NEBIUS_SA_PRIVATE_KEY` put key lines on lines of their own, which
  `cut` passes through. That happened at least three times on 30 Sep (two worker terminals, and accounting-merge's session log).

## 2. Notes: how you read and write them

- **Read:** `$RESEARCH_NOTES/kb/LANE-CONTRACT.md` (the contract), `$RESEARCH_NOTES/kb/TABLES.md` (the spec), and
  `$RESEARCH_NOTES/lanes/<any lane>/*.md` (other lanes' reports and handoffs). These are mirrors of the laptop's notes,
  refreshed about every 5 minutes. They're read-only for you, except as noted below.
- **Translate paths:** wherever a brief or handoff says `~/.research/notes/X`, read `$RESEARCH_NOTES/X`. Wherever it says a
  Project store path (`docs/...`, `internal/...`), read `$STORE/docs/...` or `$STORE/internal/...`.
- **Write:** only these.
  - Your own directory, `$RESEARCH_NOTES/lanes/<your lane>/`. Write it with the CLI:
    `research notes checkpoint <lane> open "..."`, which creates or updates your report there. The CLI works on this
    plain directory, with no git needed. Keep the notes format the CLI writes, and don't add or edit frontmatter in these
    files.
  - No handoffs: a message to another lane or the coordinator goes to your coordinator, never as a note (contract §5).
  - Scripts under your own `tools/`. Evidence (logs, JSON, plots, run outputs) goes to the evidence store only
    (`research data put --kind evidence/v1 ... --preserve`, or `research run ... --custody-r2`), cited by `art:` id:
    `research notes sync` leaves `lanes/*/evidence/` out of the notes.
- **Direct mode** (section 1): the "Read" and "Write" paths above are your clone, so reads are as fresh as your last
  `git -C $NOTES_CLONE pull --rebase --autostash`, and checkpoints and `research notes sync` push them. Still never run
  `notes push` or `notes snapshot`.
- **Fallback mode:** **don't** run `research notes sync`, `notes push` or `notes snapshot`. The coordinator mirrors your
  directory into the notes and publishes it. Your inbox (`research notes inbox <lane>`) shows the machines' notices
  once they're mirrored in.
- **Cadence:** checkpoint at least every 12 minutes while working. The mirror adds up to about 5 minutes before the
  steward sees it.

## 3. Code

- Work on branch `lane/<your lane>` from `origin/main` unless your brief says otherwise. Commit, then
  `git push -u origin lane/<lane>` after every commit. No force-push, no amend. If pushing `lane/*` is refused, push your
  agent's own branch instead, and name it in your first checkpoint.
- If your worktree is on another branch (your agent's own, say), bind it once, or `research notes push` and
  `checkpoint final --require-pushed` refuse with "no local branch lane/<l>":
  `research notes bind <lane> --branch <current branch> --worktree <dir> --pod none`.
- Merges into `main` belong to the research coordinator. Send your coordinator a merge-ready message (tip, tests, negatives, behaviour
  changes).
- Heavy builds and measurements run on pods, not on your VM, unless the brief says the VM is fine for them.

## 4. Pods

- Create them with
  `research pods create --name vy-<lane>[-<gpu>] ... --register --project verity --guard <idle minutes>`. The entry goes
  to `$RESEARCH_MACHINES_D`, which the coordinator mirrors into the notes registry, so the steward's reaper and guard see
  it. Use the cheapest pod that answers your question, and terminate it as soon as you're done
  (`research pods terminate <pod id>`; `research pods list` shows the id).
- Launch with `research run --on <pod> --project verity --custody-r2 ...`, so every run is preserved on R2 even if your VM
  goes away. The check from another machine is `research data preserved <run>`.
- Research pods are `vy-*`. Never touch `vyv-*` (the vLLM project's pods) or `vy-control-verity`.

## 4a. If your lane was FINAL and you're reopened (a re-audit, a follow-up)

The steward's reaper terminates a FINAL lane's pods, and it only sees your checkpoints after the coordinator mirrors them
(up to about 7 minutes, longer if the laptop is down). red-team-flock lost four pods this way at 12:30Z.
1. Your **first** action: `research notes checkpoint <lane> open "reopened for <why>: NOT final"`.
2. Create **no pod** until the coordinator confirms it has mirrored that checkpoint. Message your coordinator
   "REOPENED <lane>: confirm before pods". If you get no answer within 15 minutes, create
   the pod, and name it in a checkpoint at once.
3. If a pod vanishes minutes after you create it, stop creating pods and tell the coordinator.

## 5. Finishing

- Write FINAL as `research notes checkpoint <lane> final "..."`, with `--require-pushed` if you made commits. Say which
  pods you terminated and what you spent.
- Your final reply to whoever launched you: the results, artifact ids, commits, pods, spend and the FINAL line.

Times: say them in PT in prose. Keep UTC in filenames, ids and CHECKPOINT stamps.

## 6. Waiting on a pod job: end your turn (2026-09-25 17:20Z, root's rule)

The project is at Cursor's limit on concurrent cloud agents, and a running turn holds a slot. So a lane never stays in a
running turn while a pod job runs:
1. Start the job detached with custody: `research run --on <pod> --project verity --custody-r2 --custody-ttl <longer than
   the job> ...`. It returns at once, and the pod runs and records the job without you.
2. Checkpoint in this exact form, then end your turn:
   `research notes checkpoint <lane> open "WAITING <run id> on <pod>, check after HH:MMZ; agent <your bc-id>; next: <step>"`
3. The research coordinator's sweep (every 30 min) watches every `WAITING` run. When one finishes, the coordinator asks the
   root to wake you with `WAKE: <lane> <agent id> <why>`. On waking, `research fetch <run>` (records only) and carry on.

Don't poll in a loop or sleep in a turn. A job under ~2 minutes may still be awaited in the turn.

## 7. One-line rules (process-robustness, 2026-09-26; `docs/process-robustness.md`)

- **Arm your own wake timer before you end a turn.** A `WAIT … check-back HH:MMZ` checkpoint prints the delay N. Arm
  `subscribe_timer` with `once=true` and `delaySeconds=N`, and check back within the pod's idle window. Write STATE/READY
  before you sleep. The coordinator's sweep is only the backstop.
- **Stop a run by process group:** `kill -TERM -<pgid>` (the pgid is in the run's `status.json`), and a queue driver by its
  own pid. Never use `pkill -f`: it matches the runner's argv.
- **Check that a note exists after writing it:** `ls` it and name it in your next checkpoint. The store mount answers
  EAGAIN, sometimes after the write landed.
- **No cron timers.** Cursor timers are `delaySeconds` from UTC only. Recurring UTC jobs, such as renders, belong on the
  steward.
- **A failed push doesn't block you.** Commit, name the sha in your checkpoint, `git bundle create` the branch into
  the Project store's `artifacts/` (never the notes), and ask once for a token refresh.
- **Custody lifetime:** the key lasts 6 h by default. A `--timeout` longer than that needs an explicit `--custody-ttl`, up
  to 24 h, or `research run` refuses to launch it.
