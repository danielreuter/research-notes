---
id: 20261001T0215Z-handoff-from-bc-dd22acf8-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-dd22acf8 (the PoUW MVP)
---

# bc-dd22acf8 (the PoUW MVP): migration handoff. Window 8 is my one live item, and I keep driving it until it's preserved

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. I'm in its served-path exception. Window 8
(`r20261001-020519-e39d`, lease 7:20 PM PDT) is queued. I post its totals and verdicts here and then stop. Everything else I
own is done, preserved or parked. As of 7:15 PM PDT.

## 1. Branches and PRs

None of mine is merge-requested, and none is on tonight's path. The served tree is bc-ccd30e80's #596 stack
(`cursor/served-gap-profile-76ee`, then #596 `cursor/served-gap-h2-spread-76ee` `10b5526b`, then bc-b139c29c's #610
`cursor/served-h2-rows-s-b0c4` `e442d494`). That stack already contains my #540 and #564 commits.

- **#540** `cursor/pouw-rtxpro-e2e-4f91` `120c26ed`, draft, base `cursor/pouw-gpu-path-4f91`.
  - What it is: the MVP's first served path (Pearl-C sm_120 in vLLM, the pass verifier, the node-2 jobs; windows 3–5).
  - Left: nothing. Its commits are in `cursor/served-gap-profile-76ee`, so it can be closed without losing work. Daniel decides.
- **#564** `cursor/pouw-decode-deferred-4f91` `a895ade7`, draft, base #540.
  - What it is: the deferred side-stream schedule, and the hashing format as a switch.
  - Left: the switch is in #596's tree (`SCHEME`). The deferred schedule was never timed on the graphed path; that's backlog item "#578's deferred schedule". Close it, or leave it parked.
- **#589** `cursor/pouw-error-trace-4f91` `294b113d`, draft, base #540.
  - What it is: `window.sh MODE=trace`, the untimed per-linear error trace.
  - Left: nothing. Its verdict, that the quality gap is the protocol's intended noise, is in `docs/pouw/mvp-e2e.md` (top-level store). This is the only branch whose commits aren't in #596's stack, so keep it if the trace should stay runnable.
- **#600** `cursor/pouw-mvp-forms-4f91` `d765b776`: closed (GPU 1's `s,one` forms are `-h1` only). Nothing left.
- **#389** `cursor/pouw-ncp-v2-vllm-4f91` `0e0f9678` (ready, base `main`), **#435** `cursor/pouw-gpu-path-4f91` `c354ca9e` (ready, base #389) and **#433** `cursor/pouw-audit-per-forward-fp8-4f91` `7a853670` (ready, base `main`).
  - What they are: the older NCP serving stack.
  - Another agent merged `main` into all three between 7:04 and 7:08 PM PDT. That's the deployment audit's work (bc-f9184c6e, backlog "#471 / #473 / #433 / #435 / #389").
  - Left: recorded `check.py --record` runs, then merging in order #433, #389, #435. That isn't my work any more, and it's off tonight's goals.
- **#464** `cursor/pouw-hash-cut-4f91` `af5269cb`, draft, base #435: the RTX 4090 hashing cut, superseded by the sm_120 work. I'd close it.
- **#332** `cursor/pouw-gamma-pearl-fa-4f91` `189b2528`, ready, base `main` (stacked on #436): the two Pearl baselines. The backlog says to close it or leave it.

## 2. Runs and jobs in flight

- **Window 8, `r20261001-020519-e39d`, the only one.** Custody is on: `--custody-r2 --custody-ttl 8h`, `--timeout 21600`.
  - Launched at 7:05 PM PDT from a clean checkout of #610 `e442d494`.
  - Settings: `SCHEME=pearl-c-sm120-v1-h2`, `GRAPHS=1`, `FP8_GRAPHS=1`, `SCHEDULE=serial` and `ROWS_FORM=s`.
  - The ship is `SHIP_TAR=/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar`.
  - Timeline: it waits on node 2 until 7:20 PM PDT, takes `gpu-lease 8 --timed` until about 7:40 PM PDT, then verifies on the CPU. The verdicts arrive about 8:35 PM PDT.
  - Its records go to the store when it ends.
  - Its retained pass, at `/workspace/pouw/mvp-e2e/passes/r20261001-020519-e39d` (about 73 GB), isn't uploaded by custody. bc-2aa33ad8 deletes it after the rows publish.
- **Fill:** none in flight. `mvp-quality-perplexity.sh` and `mvp-error-trace.sh` are in `fill/done/`. Their outputs are in `/workspace/pouw/fill-out/mvp-quality/38f5a277/` and `/workspace/pouw/fill-out/mvp-error-trace/294b113d/`, which node 2's hourly backup covers.
- **Preserved** (`research data preserved` says PRESERVED):
  - window 7, `r20260930-221231-3dd1`;
  - the smoke, `r20260930-220851-c004`;
  - the forms window, `r20260930-202402-b130`;
  - `r20260930-195640-ee96`, `-202946-2008` and `-204754-ffe0`;
  - the forms A/B, `r20260930-202418-deee`, which I fetched just now: preserved=yes.

## 3. Half-done state

- **VM-only material is now copied.** `window7.sh`, `window8.sh`, `forms_ab.sh`, `prio.py`, `prio-window.sh` and `prio-test/` are in the store's `internal/pouw/rtx-pro/workers/pouw-mvp-e2e/`. The scripts are also on node 2 in `/workspace/pouw/mvp-e2e/`. The VM's worktrees are all clean, with everything pushed, so nothing else lives only here.
  - `window8.sh` is the template for any later window: it waits until `START` (UTC), takes `gpu-lease 8 --wait --timed --max-min 20 -- timeout 1140 window.sh`, validates, then runs `verify.sh <run id> 48`.
  - The launch command is in `server.md` (7:08 PM PDT) and section 2 above, with `--send window8.sh -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/window8.sh"'`.
- **Node 2's `/workspace/pouw/mvp-e2e/`** is setup.sh's `$WORK`: `venv312`, `models/llama-3.1-8b-instruct`, `ready.json` and `passes/`. Keep all of it, because `window.sh` refuses to run without `ready.json`.
- **The retained passes,** about 73 GB each, 11 of them:
  - Mine are `r20260930-202402-b130` (the forms window, verified; deletable now) and `r20260930-221231-3dd1` (window 7; bc-2aa33ad8 deletes it as chain step 2, and it was still there at 7:12 PM PDT).
  - bc-ccd30e80's: `a898`, `4306`, `c584`, `b671`, `fcc0`, `13ef` and `9241`.
  - bc-b139c29c's: `a3d0` and `35d9`.
- **The ships:**

  | Ship | Path on node 2 |
  |---|---|
  | ship3 | `/workspace/research/runs/r20260930-141053-b3c0/inputs/pearl-c-sm120-ship.tar` |
  | ship15 | `r20260930-175714-aced/inputs/pearl-c-sm120-ship15.tar` |
  | #596's | `r20260930-185328-e6ac/pearl-c-sm120-ship.tar` |
  | #610's | `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar` (sha256 `561de725…`) |

- **Documents:** the MVP's write-up is `docs/pouw/mvp-e2e.md` in the top-level store (Status block, window 7's section, "The next run", quality). My status file is `internal/pouw/rtx-pro/workers/pouw-mvp-e2e.md`.

## 4. The next step for each kept item, and what to stop

- **Window 8** (backlog "window 8", mine until it's preserved; then my successor):
  1. When the lease ends, post the totals here and in `server.md`, from the run's `e2e.json`, as for window 7.
  2. When the verify ends, post the four verdicts.
  3. bc-ccd30e80 makes the rows (`panel_rows.py`, window 7's recipe).
  4. bc-2aa33ad8 appends and renders them, runs `ov-sync`, and deletes the pass.
  5. bc-824e54a2 pushes the labels (the 6:04 PM PDT chain).
  6. Then add a window 8 section and Status line to `docs/pouw/mvp-e2e.md`.
  - If the verify fails or misses 11:40 PM PDT, window 7's row (attempt 109) stands.
- **Goal 2 (window 7's totals):** done. Nothing left.
- **#540, #564 and #589** (backlog "MVP drafts", which Daniel decides): my view is to close #540 and #564, whose work is in #596's stack, and to close #589 or keep it as the trace's record.
- **#389, #435 and #433:** with the deployment audit. Nothing from me.
- **#464 and #332:** I'd close both.
- **MKL race** (the 6:10 PM PDT order): not exposed. A grep of `benchmarks/pouw/pearl_c_vllm/` and `protocols/pouw/` at `e442d494` finds no torch transcendental, and `verify_run.py` doesn't import torch.
- **Stop:** more `-h1` hashing-form experiments on the served path (dropped), repeats of window 7, and the deferred schedule on #564's old tree.

## 5. Traps

- **Launch from the PR head's checkout, not an old `/workspace`.** `/workspace`'s `research` (Sep 28 `main`) has no custody flags. `uv run research …` in the PR's checkout builds that tree's `research`, which defaults to custody on the store's remote.
- **Reading the CLI's options.** `research run --help` only prints "the workload command goes after `--`", so read `tools/research/src/research/cli.py` instead.
- **The passes aren't in custody.** They live in `$WORK/passes/<run id>`, outside the run directory, so custody doesn't upload them. `verify.sh` finds them by run id. Delete one only after its verify and rows are done.
- **Verify after the lease, never beside a timed window.** Node 2's quiet guard freezes CPU work during timed leases, which is why `window8.sh` verifies only after the lease. A 48-process verify beside a window also skews that window's timing: bc-b139c29c's 28.3 ms decode was taken beside window 7's verify.
- **`--no-sampler`** on any `research run` that holds a timed lease.
- **The ship must match the tree.** `window.sh` compares the ship's `run.py` with the tree's `benchmarks/pouw/pearl_c_sm120/run.py` and fails `WINDOW_FAIL_SHIP` if they differ. A change to that file needs a new ship from GPU 1's `build.sh`.
- **Don't mix the hashing forms.** `ROWS_FORM=s` is refused under `-h1`, and GPU 1's `PEARLC_A_FORMS=s,one` is `-h1` only.
- **`jit-built.txt` must be empty.** A FlashInfer JIT build inside the window fails validation, so use setup.sh's `venv312` (`window.sh` puts it first on `PATH`).
- **`panel_rows.py --by` defaults to bc-dd22acf8** (`PANEL_BY`). Set it for anyone else's window.
- **Editing `server.md`.** New entries go below the pinned block, newest first, and line numbers shift while others write, so anchor edits on a heading's text. The Grep tool doesn't search the store, so use `rg` in a shell. Node 2 has no `rg`; use `grep` there.
- **Timers.** Unsubscribing a past-due timer can return `closed: false`, and it still fires later with stale instructions. Read the current orders before acting on a timer's prompt.
- **research-notes.** Commit, `git pull --rebase`, then `git push origin HEAD:main`. On a 403, stage in the store's `internal/pouw-fp8/accounting-outbox/`.
