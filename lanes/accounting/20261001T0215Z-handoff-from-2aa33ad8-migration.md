---
id: 20261001T0215Z-handoff-from-2aa33ad8-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-2aa33ad8 (RTX PRO coordinator, node 2 vy-nebius-2); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff: the RTX PRO (sm_120) PoUW coordinator, bc-2aa33ad8 (7:15 PM PDT, 30 Sep)

What I do: drive GPU workers 0–7, the harness and its helpers on node 2; own the panel (`internal/pouw/panel/`); own the worker
channel `internal/pouw/rtx-pro/server.md`; launch the timed canary and repeats; queue approved fill. Every store path below is in
the top-level Agent Store `bc-b729c175…` unless it says "node 2".

## 1. Branches and PRs (all open drafts; each worker owns its day-to-day; heads at 7:10 PM PDT)

| PR | Branch | Head | Owner | State and what's left |
|---|---|---|---|---|
| #580 | `cursor/pearl-c4-f1f2-3084` | `639128c87` | GPU 5 bc-71c6ab78 | F1′, R1, tightened D-NF, pinned c_L, the 8-block rotation + V/O/interleave registration rule (6:40 PM PDT); 1,691 tests pass. *(Corrected 7:12 PM PDT, from GPU 5's handoff: B-OVF is already in, via merge `fb251c6e`, vectors regenerated `7a75614a`.)* Left: take #556's head `9363e5012`, `check --record`, then a train with #556 |
| #548 | `cursor/pearl-c-fp4-3084` | `7a30515b7` | GPU 5 | check passed (`r20261001-000221-f7ef`, the MKL warm-up merged); ready for a train |
| #491 | `cursor/pouw-harness-sm120-d2f2` | `aa4f95db9` | harness bc-0de2d624 | dropped-names run fails (`9db36fe7d`); each library's best timed and chained (`88ef0927b`); 233 pass |
| #588 | `cursor/harness-helper-cd3d` | `dd23c0c36` | harness helper bc-6da61042 | #588's plain-GEMM divisors; merges #491 cleanly (243 pass on the merge) |
| #570, #543, #529 | `cursor/fp8-plain-mainloop-0be9`, `cursor/nvfp4-mainloop-0be9`, `cursor/pearl-c-fp8-mainloop-0be9` | `025cc1f8a`, `549313d49`, `e0e84b25d` | mainloop lane bc-fb55a759 | plain FP8 GEMM (`_ew` 1.4148 ms is the fastest FP8 8,192³ divisor), NVFP4 mainloop, Pearl-C FP8 mainloop |
| #507, #505 | `cursor/pearl-c-sm120-attacks-cb92`, `cursor/pearlc-activations-layers-cb92` | `854749912`, `548363f43` | GPU 3 bc-0f3f8a2f | `hot_blocks.py`, `padded_floor.py` (Results 21–23) |
| #506 | `cursor/pouw-hash-sm120-9569` | `4a4fde4f9` | GPU 2 bc-7442ca43 | hashing; the `-h2` bench is on `cursor/h2-hash-bench-9569` |
| #525 | `cursor/fp4-capture-sm120-9ff9` | `6ed30ed68` | GPU 4 bc-36186951 | FP4 capture and verify |
| #545 | `cursor/fp4-attack-quality-60ef` | `f08225201` | GPU 7 bc-dbc19788 | 70B FP4 GPU census port (`4f406662`, `141b552e`, `f0822520`) |
| #492 | `cursor/sm120-fp8-capture-75d4` | `7aa3abf63` | GPU 0 bc-e6a46970 | GPU-side step-model check (`fp8_check.cu`) |
| (GPU 1's) | `cursor/pearl-c-sm120-h2-arm-b44b` | `a00db59e` | GPU 1 bc-18346d9c | the `-h2` arm, timed (attempts 105, 106) |

## 2. Runs and jobs in flight

- **Research runs I launched:** my VM has no store remote, so all of these are `--no-custody-r2` and need preserving by hand.
  - **`r20261001-014542-2892`:** the 6:30 PM PDT attempt-67 repeat. *(Updated 7:20 PM PDT.)* Done: prefill 1.8018× and 1.7657×,
    −0.14% and −0.05% from the pilot, inside the spread; decode −1.53% and −1.56%, unexplained (load was low, mean 18). Posted in
    `server.md` 6:57 PM PDT and `note:20261001T0222Z-reply-from-2aa33ad8-repeat-second-sample`; staged in
    `internal/pouw/rtx-pro/fill-out/a67-repeat-r20261001-014542-2892/`, needing `research data put --preserve`.
  - **Window 8, `r20261001-020519-e39d`** (bc-dd22acf8's, not mine): #610 `e442d494`, timed lease 7:20–about 7:40 PM PDT, verify
    until about 8:35 PM PDT. bc-c62f9726 (`pouw-served`) takes it over once preserved; its rows go to the node-2 lead (`pouw-node2`)
    for the panel append, by window 7's recipe (`internal/pouw/rtx-pro/window7-panel-rows.txt`).
  - **`r20261001-004424-7b1f`:** the canary, done and staged in `fill-out/a67-canary-r20261001-004424-7b1f/`. It needs `research data put --preserve`.
- **Fill jobs I queued** (node 2's hourly backup preserves `/workspace/pouw/`):
  - `gpu3-fp8-padded-hot.sh` and `-hot-cancel.sh` (owner GPU 3), the padded re-search (a). Output `/workspace/pouw/gpu3-fp8/out/padded-hot{,-cancel}/`. Ends about 9:45 PM PDT to midnight. **Stop it at once if fix (2) fails** (compute-accounting, 0111Z).
  - `pearlc4-vex-coverage.sh` (owner bc-a8466279), V-EX coverage. Output `/workspace/pouw/pearlc4-cpu-fill/vex-coverage/<capture>/`, about 4 CPU-h; 3B at 188 tiles at 6:30 PM PDT, 7B next.
  - `pearlc4-bovf-strong-search.sh` (prio 5) and `f5bf-fp4-coverage-70b-cpu.sh` (prio 0) are queued and not started; the pous CPU slots are full.
- **Workers' own fill:** GPU 7 `fp4-cov70b-*` (about 6.5 GPU-h, `/workspace/pouw/gpu7-fp4/cov70b/4f406662/`; salts 8–15 exceed the approved 5 GPU-h, ask open with you); GPU 0 `fp8gc-die*` (about 5 GPU-h, `/workspace/pouw/fill-out/fp8-gpucheck/`); GPU 2 `gpu2-h2hash-die*` (about 8.7 GPU-h).
- **Done, outputs staged in the store, needing `research data put --preserve` (bc-824e54a2):** `fill-out/fp4-dnf-replay-audit/` (the D-NF replay passed, 5:59 PM PDT); `fill-out/a67-canary-…/`.
- **Done, outputs in the store** (`internal/pouw/rtx-pro/catalogue-audit/node2/`): `v1-closure-full-catalogue/`, all 10 regions equal to the copy, whole unit 1.0128.
- **My workers' handoffs (7:20 PM PDT):** GPU 0, 1, 2, 4 and 5, the harness and both helpers have filed theirs. GPU 7's
  (`bc-dbc19788`) is staged in the outbox for the relay. GPU 3 (`bc-0f3f8a2f`) hasn't filed one; it's mid-turn, and I'll resume it
  with the pointer when the turn ends. Fix (2)'s judging job `gpu3-fp8-fix2-blocks.sh` started 02:12Z (starts 0–5); window 8's
  lease pauses it, so its verdict lands after about 7:40 PM PDT.

## 3. Half-done state

- **The panel** (`internal/pouw/panel/`):
  - `lines.json`, `attempts.jsonl` (append-only, corrections applied on read), `ov-synced.jsonl`, `panel.py`, rendering `docs/pouw/panel.md` and `media/pouw-slowdown-*.png`.
  - **Render:** `VERITY_REPO=<a checkout with benchmarks/pouw/harness/ledger.py> python3 panel.py render`. I use `/tmp/harness-helper`, #588's branch; without it the evidence-store rows drop.
  - **ov-sync:** `python3 panel.py ov-sync --research-cmd "uv run --quiet --project /workspace research"`.
  - **The label export:** `internal/pouw/panel/ov-labels/labels/<run>/`, for a VM with the store remote to `labels-sync --from-dir`. 25 rows are publishable, attempt 109 (window 7, goal 3) is labelled and exported, and step 3 (the push) is bc-824e54a2's.
- **The worker channel:** `internal/pouw/rtx-pro/server.md`; each worker's status is in `internal/pouw/rtx-pro/workers/*.md`.
  - **Pinned at the top:** compute-accounting's handover order (6:28 PM PDT); the custody rule and the spool; the MKL `exp` warm-up check (6:10 PM PDT); GPU 3's v2-hot orders.
- **Copied from my VM to the store:** `internal/pouw/rtx-pro/coordinator-tools/`. It has `insert_entry.py` and `move_top.py` (`server.md`), `a67-canary-job.sh`, `a67-canary-watch.sh` and `a67-repeat.sh` (the canary, launched like the pilot `r20260930-174917-2585` with its seven inputs; the inputs are also in node 2's run dirs), `dnf-*`, and `v1-closure-copyback.sh`. The sharded closure code is in `catalogue-audit/node2/src/`.
- **Only on my VM, and reproducible:**
  - the source worktree `/tmp/a67src` at `0cb23bfd` (`git worktree add`);
  - the research CLI's ssh key copy `~/.runpod/ssh/runpodctl-ssh-key`, a copy of the research key, not to be copied;
  - my local evidence store `~/.research/store`. Its `ov.*` labels are exported to the store above, and the canary run is copied.
- **The window plan** (pinned 3:12 PM PDT list, updated): the repeat is now; then `-h2+s` (#610, bc-dd22acf8 claims it); then the
  divisor window (my ask `20261001T0135Z…`, about 0.25 GPU-h, harness staging, waiting on your YES).

## 4. Next step for each kept item; what I'd stop

- **The repeat:** read (above). Left: preserve it, and node2-ops (bc-c0738ef6) says what fill was live during it, since it's their A/B.
- **The panel against the assumption table:** bc-69c09d42's handoff lists seven panel/table differences (its table's §5) for me;
  I didn't get to them. Recheck them against `lines.json`, which has since moved v2-hot off the plots.
- **Goal 3:** after bc-824e54a2's push, check that @console shows attempt 109 (3.4024× graphed, 1.2629× eager beside it).
- **v2-hot:** GPU 3 runs fix (2) (0111Z). If it fails, stop (a), and v2-hot is parked. If it passes, bc-b58c6093 restages, and `v2-hot-16384` waits for a new order.
- **The divisor window:** on your YES, the harness queues it. Adopting the divisor needs the confirming row: FP8 `_ew`, NVFP4 `_o_ew`.
- **The MKL race:** collect each lane's "not exposed" or warm-up line. The leads are `f5bf-fp4-coverage-70b-cpu.sh` and `pearlc4-bovf-strong-search.sh`.
- **The panel:** keep v2-hot off the plots, and v1 at 0.519% as the only FP8 line under 1%, until compute-accounting rules otherwise.
- **I'd stop:** `floor-staircase-fine.sh` (GPU 3's clause (c) check covers it); v2's region-row re-search `gpu3-fp8-padded-zero.sh`, NO already; any further `hsplit` (withdrawn, finals for 17 shapes); per-die form repeats and hash benches beyond what's running.

## 5. Traps

- **The store mount** returns EAGAIN and I/O errors under load. Use retry loops and temp-then-rename writes; never trust a single `cp`.
- **`panel.py`:**
  - `append --change` takes only `baseline`, `kernel` or `protocol`.
  - Give a window's rows one `--attempt N`. The raw log holds rows 107 and 108, renumbered to 105 and 106 by corrections, so don't reuse 107 or 108.
  - `ov-sync` keys by shape since 5:48 PM PDT, so twin rows (graphed/eager) get shape-qualified refs.
  - Labels written on a VM without the store remote are local only, so export them.
- **The fill runner** clamps a pous job's `max_min` to 30 and restarts it from the top; long single tasks livelock, so shard them, as for v1-closure.
  - pous CPU fill is pinned to 96–127, which is NUMA 1. GPU fill jobs share those cores and get starved; GPU 7 saw 4–9× slowdowns.
  - `--membind=1` (node2-ops) is strict: a job that outgrows NUMA 1 is OOM-killed.
- **Timed windows freeze only fill:** a research-run verify on the CPUs (window 7's, 48 workers) ran unfrozen beside the canary. Check before launching a timed window.
- **The canary's like-for-like reference** is the pilot `r20260930-174917-2585` (GPU 0, `algo35_tile20`), not attempt 67's first run (`-122529-fb8b`: GPU 1, older harness, `tile23`).
- **Resuming a worker:** pass the full id with its `bc-` prefix. Without it the Task tool starts a fresh stray agent (it happened once, at 3:54 PM PDT; the stray did nothing).
- **The research CLI** looks for its ssh key at `~/.runpod/ssh/runpodctl-ssh-key`. Without a store remote, a run needs `--no-custody-r2`, or now the spool.
- **The D-NF summary's lines start with a timestamp,** so `grep '^DONE'` misses. My watcher misreported the pass for that reason, and I corrected it.
- **Notes pushes after a VM reset:** the git config rewrites GitHub URLs to the bot's token, and the notes repo refuses it (403). Use a credential helper with `RESEARCH_NOTES_TOKEN` (GPU 5's fix).
- **Node 2 stops at 7:55 AM PDT on 7 Oct.**
