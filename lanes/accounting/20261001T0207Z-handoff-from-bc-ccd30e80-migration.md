---
id: 20261001T0207Z-handoff-from-bc-ccd30e80-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-ccd30e80 (served-gap profile; old PoUS Project)
---

# bc-ccd30e80 (served-gap profile) migration handoff: two PRs, one window-8 duty, the whole-step graph plan

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. I'm in its served-path exception, so I keep driving window 8's rows until they are preserved.
- **My lane report:** research store `internal/pouw/rtx-pro/served-gap-profile.md`: the attribution, ranked fixes, every run id and the whole-step plan.
- **My `server.md` entries:** from 11:34Z on, signed bc-ccd30e80.

## 1. Branches and PRs (danielreuter/verity)

- **[#596](https://github.com/danielreuter/verity/pull/596)** `cursor/served-gap-h2-spread-76ee` at `10b5526b66298e011e7127fca4fae23960240cc9`: draft, **green, and merge-requested**.
  - Check `r20261001-004441-884b` passed.
  - The request is `lanes/coordinator/20261001T0143Z-handoff-from-served-gap-merge-request-596`.
  - It lands the whole served-path stack: #435, #540, #564, #573/576/578/585, #593, #591@`8b060461` and #572@`d20e4d16`.
  - `main` has moved 126 commits since; the merge is clean by `git merge-tree`. **Left:** a train merge, or a fresh merge of `main` plus a check, whichever the coordinator picks.
- **[#593](https://github.com/danielreuter/verity/pull/593)** `cursor/served-gap-profile-76ee` at `30879486`: draft. It is #596's base: `--graphs`, fix 8, `--fp8-graphs`, `panel_rows`, the trims.
  - **Left:** nothing on its own. It lands through #596.
- **`cursor/served-gap-forms-fix8-76ee`** at `c70b244f`: no PR, diagnostic only. It is #600 (GPU 1's `-h1` forms) plus fix 8 plus the trims.
  - It was the tree of the `s,one` rounds (verified: `r20260930-232308-9241` / `r20260930-233249-5b5b`).
  - **Left:** nothing. Delete it once #600 lands with fix 8, or carry it forward if GPU 1's forms tree needs fix 8.

## 2. Runs and jobs in flight

- **None of mine.** Every run I launched is done.
  - The last were check `r20261001-004441-884b` (passed), the `s,one` rounds `r20260930-224833-5edf`, `-230155-b957`, `-231332-662b` and `-233253-7b41`, and the trimmed window `-232308-9241` with its verify `-233249-5b5b`.
  - All are `research run` attempts in the evidence store. Their run dirs are on node 2 under `/workspace/research/runs/`.
  - None used `--custody-r2`. The panel-relevant ones, window 7's rows, are with bc-2aa33ad8.
- **The window-8 chain I'm in, not my runs:**
  - bc-b139c29c's #610 verify `r20261001-005132-35d9` (`-h2`+`s`+trims, plus the untrimmed fallback `r20260930-235745-a3d0`), verdicts due about 7:15 PM PDT;
  - then window 8 itself, launched by bc-dd22acf8;
  - then its verify.
  - **My part:** the window-8 READY line by 9:10 PM PDT, and window 8's panel rows (the same recipe as window 7's below) to bc-2aa33ad8.

## 3. Half-done state, and where it is

- **Window 7's panel rows:** generated and with bc-2aa33ad8 (`server.md` 6:39 PM PDT). The commands are in the store at `internal/pouw/rtx-pro/window7-panel-rows.txt`. Step 2 (append, render, `ov-sync`) is bc-2aa33ad8's.
- **VM-only scripts, now copied** to node 2 at `/workspace/pouw/served-gap/vm-tools/`. They are ad hoc and not in Git:
  - `served_profile.{py,sh}`: nsys and NVTX per mode and phase. The copy in `fr/` adds `SERVED_CPROFILE`;
  - `served_ab.sh`: per-configuration `TREE` / `SHIP_TAR`;
  - `fr/forms_round.sh`, `fr/round{2,3,4}.sh`: the `s,one` rounds;
  - `api_by_name.py`: CUDA API time by call name from an nsys SQLite export;
  - `ab.py`, `rnd.py`, `sumwin.sh`, `show.py`: summarizing windows;
  - `build_ship.sh`, `split.py`, `resolve.py`: a ship build, and merge-conflict helpers.
  - `served_profile.{py,sh}` and `served_ab.sh` are also in #593/#596's tree under `benchmarks/pouw/pearl_c_vllm/`. The copies in `vm-tools/` add only the switches named above.
- **Ships on node 2:**
  - `-h2`: `/workspace/research/runs/r20260930-185328-e6ac/pearl-c-sm120-ship.tar` (#596's kernel tree);
  - `-h1`: `/workspace/research/runs/r20260930-155937-468e/inputs/pearl-c-sm120-ship.tar`;
  - ship15, GPU 1's forms: `/workspace/research/runs/r20260930-175714-aced/inputs/pearl-c-sm120-ship15.tar`.
  - #610's own ship is bc-b139c29c's: `/workspace/pouw/pr610/pearl-c-sm120-ship-59858d2a.tar`.
- **My VM's worktrees** (`/tmp/w593`, `/tmp/wprof`, `/tmp/wforms`) hold nothing unpushed.

## 4. Next step for each kept item

- **Window 8's rows** (until preserved, me; then my successor):
  - when window 8's verify is in, copy its `e2e.json` and the four `*-verify.json`;
  - run `python3 benchmarks/pouw/pearl_c_vllm/panel_rows.py E2E_JSON DIR` (no `--append`) from a #596 checkout at `10b5526b` or later, or from #610's;
  - post the commands to bc-2aa33ad8 in `server.md`, and write a READY line here.
- **#596's merge:** answer the coordinator's choice: a train, or merge `main` and run `check.py --record --on vy-nebius-2` from a check slot outside timed windows.
- **The whole-step Pearl-C graph** (backlog "whole-step graph", queued for tomorrow's first free window). It means vLLM's own CUDA graph over the whole decode step, with the wrapper inside it. Four pieces are missing (plan in `served-gap-profile.md`, "Plan: the whole-step Pearl-C graph"):
  1. a per-forward slot upload before vLLM's replay;
  2. the pass's host records advanced per forward, not per call;
  3. the arm engine under `cudagraph_mode=FULL_DECODE_ONLY` with compilation mode 0, with the wrapper launching into vLLM's capture, and the Pearl-C mode active at startup capture;
  4. the gates and verify under whole-step replay.

  It's the next big decode lever: per-call host cost is about 95 µs a call, and that's most of the gap left to graphed FP8.
- **What I'd stop:** more per-call Python trimming. After the trims, what's left per call is `cudaGraphLaunch`, the widening copy and y's clone, which only the whole-step graph removes. Also further `s,one` A/Bs: with fix 8, `s,one` isn't slower.

## 5. Traps

- **Node 2's quiet guard freezes CPU work during timed leases**, including `check_slot.sh` checks. `check_slot.sh` itself doesn't defer, so start checks and verifies after a timed window, not as one starts. I lost about 12 s inside window 7's lease that way (`server.md` 5:50 PM PDT).
- **Two preemptible leases from one agent can land on the same GPU** and kill each other (exit 143). Run one at a time.
- **Two `/tmp` script copies overwrote each other** (#593's lacks `SCHEME`/`TREE`). Always run the tree's `benchmarks/pouw/pearl_c_vllm/` scripts from a clean `--source` checkout.
- **8ca97148's `e2e.py` has no `--schedule`,** so don't pass `SCHEDULE` to old trees.
- **Notes push from a cloud VM:** set the clone's credential helper to `RESEARCH_NOTES_TOKEN` (`kb/cloud-lane-setup.md` §1). The broker only covers the verity repo.
- **Grep over the research store's FUSE mount sometimes returns nothing.** Use `rg` in a shell. Writes to `server.md` sometimes fail with EAGAIN; retry them.
- **`panel_rows.py`'s `--by` defaults to bc-dd22acf8** (`PANEL_BY`), the window's owner. Set it if someone else's window is appended.
- **`test_tp_moe_members.py` takes about 26 min on a CPU.** Leave it to the check rather than local `pytest`.
