---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20261001T0203Z-handoff-from-bc-b139c29c-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
---

# Migration handoff from bc-b139c29c (hash-cut change-3, `-h2` and the `s` form), 7:03 PM PDT

Per `20261001T0157Z-order-from-compute-accounting-all-migration-handoff.md`. I'm under its served-path exception: I keep driving window 8 until its results are preserved. My replacement shadows me until then.

## 1. Branches and PRs

| PR | Branch | Head | State | Left |
|---|---|---|---|---|
| [#610](https://github.com/danielreuter/verity/pull/610) | `cursor/served-h2-rows-s-b0c4` | `e442d494` | draft; READY for window 8 (7:02 PM PDT) | Window 8. It merges with #596's stack after the Pearl-C chain; rebase on #596 whenever #596 moves |
| [#572](https://github.com/danielreuter/verity/pull/572) | `cursor/pearl-c-sm120-h2-switch-b0c4` | `9288c339` | ready; check `r20261001-000957-7d55` passed; merge-requested; vLLM grant requested | After #449 → #548 → #534 land: merge `main` (115+ commits behind) and run a fresh check; then the coordinator's `research merge` |
| [#591](https://github.com/danielreuter/verity/pull/591) | `cursor/pearl-c-sm120-h2-fused-keys-b0c4` | `ac931641` | draft, on #572 at `d20e4d16` | Merge #572's `9288c339`. Decide whether it lands, since its kernel already rides #610 |
| [#533](https://github.com/danielreuter/verity/pull/533) | `cursor/pearl-c-h3-b0c4` | `658806df` | draft | Daniel's `-h3` decision, after RowSeed |
| [#532](https://github.com/danielreuter/verity/pull/532) | `cursor/pearl-c-h2-b0c4` | `d982d418` | draft | Its content rides #540 and #572: close it when #572 lands |
| [#475](https://github.com/danielreuter/verity/pull/475), [#468](https://github.com/danielreuter/verity/pull/468), [#436](https://github.com/danielreuter/verity/pull/436) | `cursor/pouw-only-bench-b0c4`, `cursor/pouw-hash-cut-change3-b0c4`, `cursor/pouw-hashing-in-headline-b0c4` | `cc485a8d`, `690f16e3`, `79b877bc` | two drafts, and #436 open on `main` | Backlog line 153: drop, close or leave |

- Already closed: #555, #549, #547, #544, #541, #537, #510.
- **Never pushed:** the VM's `/workspace` branch `cursor/pearl-c-epilogue-hash-b0c4`, five untracked files from the 30 Sep 04:06Z TurboSHAKE epilogue-hash draft, superseded. They're preserved in `art:61934edf635730ab76fc1a1720853f67abfece44834f2d9c0c3d60394d73f370`.

## 2. Runs and jobs in flight

**None of mine is running.** All of the following are done and fetched with `--all` (custody is the default):
- `r20261001-005132-35d9`: #610's untimed window with the trims and its verify. ACCEPT, ACCEPT, REJECT, REJECT, and the fallback's verify too.
- `r20260930-235745-a3d0`: the untimed `-h2` `s` and `w` windows, 5:15–5:24 PM PDT.
- `r20260930-232607-8696`: the `s` kernel's bit-exact probe, `art:b881933d…221f`.
- `r20261001-000957-7d55`: #572's check.
- `r20261001-000158-0c6d`: a verify I cancelled on purpose, rc 143.

**Window 8** is bc-dd22acf8's run, launched from `e442d494`. It hadn't launched as of 7:03 PM PDT.

**On node 2** (no custody; delete by hand when done):
- `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar`: window 8's ship. Keep it until window 8's row lands.
- `/workspace/pouw/mvp-e2e/passes/r20261001-005132-35d9` and `.../r20260930-235745-a3d0`: the retained passes, about 45 GB each, already verified. They can go once window 8's row lands.

## 3. Half-done state

- **VM worktrees, all pushed:**
  - `/tmp/wt-596s` (#610);
  - `/tmp/wt-572` (#572, with a `.venv`; I run `research` from here);
  - `/tmp/wt-540` (#591, with a `.venv`).
- **VM-only material** is copied into `art:61934edf…`, with a README inside:
  - the run scripts `h2s_served.sh`, `h2s_trims.sh` and `h2s_verify.sh`;
  - the forms probe;
  - a `uv` shim for `build.sh`;
  - the untracked epilogue draft.
- **Store reports (mine):**
  - `internal/pouw/rtx-pro/sm120-h2-switch.md`: #572, #591 and the `s` form, from 2:20 PM PDT on;
  - `internal/pouw/rtx-pro/hashing-forms-by-shape.md`;
  - `internal/pouw/rtx-pro/handoffs/hashing.md`.

## 4. Next steps, and what I'd stop

- **Window 8 (the 11:40 PM PDT goal):**
  - bc-dd22acf8 launches it from `e442d494` with window 7's switches, plus `ROWS_FORM=s` and `SHIP_TAR` as above.
  - After its verify: the rows through bc-ccd30e80's `panel_rows.py` and the chain in `20261001T0104Z-order-from-compute-accounting-panel-publish-chain.md`.
  - I watch it until its results are preserved.
- **The served stack** (#596 → #610, then #572 and #591): merge after the Pearl-C chain, keeping #610 rebased on #596.
- **Optional, not goal-critical:** `-h2`'s `one` tree, about 2.1 ms a prefill pass. It needs GPU 1's `h1_tree` on the `-h2` line.
- **I'd stop** #475, #468, #436 and the closed experiment PRs. #533 waits for Daniel's `-h3` call.

## 5. Traps

- **P10's 800-line cap.** `pouw_pearl_c_device.py` is 797 lines on #610, so almost any addition needs another split.
- **The ship must match the tree.** `window.sh` refuses a ship whose `run.py` isn't the run tree's.
  - Rebuild with `build.sh` whenever `pearl_c_sm120/run.py` or a kernel source changes. Locally that's `CUDA=/tmp/cuda-13.0.1`.
  - `build.sh`'s `uv run` wants a synced env: use the shim in `art:61934edf…`, with `PATH=shim:venv/bin` and `PYTHONPATH` set to the tree's packages.
- **Python 3.14 on node 2.** A `multiprocessing.Pool` defaults to forkserver, and a Pool over a path-loaded module hangs. Use `get_context("fork")`.
- **Verifies take time.**
  - `verify.sh` takes 35–45 min at 48 jobs, and longer beside another verify.
  - Don't run one during a timed window.
  - Untimed eager ms are noisy while a verify runs: the eager modes slowed about 35%, and only the graphed modes are stable. #610's 28.3 ms trims decode figure is contaminated that way; don't cite it.
- **`gpu-lease`:**
  - Timed leases show `timed=1`.
  - The agent may hold a grant for a few minutes after a timed window.
  - Retained passes are about 45 GB per window.
- **Bash:** `${VAR:?msg}` breaks when `msg` contains an apostrophe.
- **Tooling:**
  - Run `research` as `uv run --no-sync research …` from `/tmp/wt-572`, with `RESEARCH_MACHINES_D=~/.research/notes/machines.d`. The `/workspace` venv's `research` doesn't read `machines.d`.
  - Before a push, put `/workspace/.git/verity-auth/bin` first on PATH, and unset `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0` and `GIT_CONFIG_VALUE_0` (the broker).
  - research-notes is a sparse checkout: `mkdir -p` the lane dir, use `git add --sparse`, and read others' files with `git show origin/main:path`.
