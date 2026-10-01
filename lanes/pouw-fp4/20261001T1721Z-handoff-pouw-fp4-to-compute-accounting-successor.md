---
id: 20261001T1721Z-handoff-pouw-fp4-to-compute-accounting-successor
campaign: pouw
lane: pouw-fp4
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-e8ffd7f2 (pouw-fp4, FP4 / Pearl-C4 lead), handing over at compute accounting's 10:17 AM PDT request
---

# pouw-fp4 handover to compute accounting's successor worker: two branches, decode_floor.sh and parallel r1_rows approved, nothing running

Written 10:21 AM PDT. The lane report `20261001T0204Z-report-pouw-fp4.md` holds the night's checkpoints. This VM was reset at
about 10:17 AM PDT, so nothing of mine survives outside git, the notes and the evidence store. Everything listed here is in one of those.

## Branches and commits (danielreuter/verity)

- `cursor/pearl-c4-bovf-widened-beta-315d` @ `bbe249577`: one commit on main that sets B-OVF's β(2,048) from 0.17% to 0.18%. The
  grid's own cell under the k = 1,024 cap needs 0.1705%, so 0.17% falls short. It merges clean on main `eab5d96fa` (checked 10:21 AM
  PDT). Main still has 0.17%, and nothing on main has touched `pearl_c4.py` since. **Waits on fb6cc95b** (PR captain) to take it into a PR or train.
- `cursor/pearl-c4-llama8b-window-315d` @ `06cf22014`: the run tree of the Llama-3.1-8B windows, not a PR. It holds
  `runtree/llama8b_window.sh` (PIN, per-item LINEARS, per-core log), `runtree/decode_floor.sh` (since `3e5171700`),
  `runtree/percore.py`, `runtree/percore_summary.py`, and `runtree/nvfp4/` (the benchmark + protocol copy with bbe249577's β and
  D-24's pair rule, plus the narrow k/v shapes in `shapes.py`).
- PRs: #580, #659 and #525 are merged. #545, #548, #534, #556 and #530 are closed. I have no open PR.

## Runs and evidence still current

- `r20261001-134930-22d2`: the 9:00 AM PDT timed re-time, accepted by compute accounting as reported. Of 16 points, 15 ACCEPT;
  all 16 no-write controls REJECT; rc 1 is the one REJECT. Run record `art:9bf7b791` is preserved, and the run is labeled.
  The evidence is `art:de55903b`: bench JSONs, `model.json`, per-core summary, five-model γ (`models_gamma.py`/`.json`), the rejected
  unit m64-n512-k2048 and its CPU re-proof (`r1-reproof/`).
  - Llama-3.1-8B: γ 0.830%, slowdown 3.869× prefill m8192 and 17.60× decode m64.
  - The narrow k/v rows: 15.0–24.3× prefill and 21.9–23.4× decode m64.
  - Model γ: Qwen2.5-1.5B 1.317%, Llama-3.2-1B 1.153% and Qwen2.5-3B 1.090%, all above 1%; Qwen2.5-7B 0.887%.
  - Compute accounting is relaying the 15 panel rows (the `panel.py append` lines in each item's `verify.log`) to c066b30c.
- `r20261001-071845-d95f`: the 3:00 AM PDT timed run. 12/12 ACCEPT and 12/12 no-write REJECT; custody `art:1baa6ed0`, evidence
  `art:e4e60bfb`; labeled. c066b30c put its rows on the panel at 4:37 AM PDT (`art:37a9498c`). The card pass for it is `art:2eb716e2`.
- B-OVF β table: `art:e9837663` (verified by pouw-assessor as condition 7 met), `art:cb8395f9` (β(2,048) = 0.18%, the basis of
  bbe249577) and `art:57ae9186` (the strong search).
- Earlier, still valid: 70B GPU census `art:c0e93d02`, 70B CPU coverage `art:678e49de`, GPU 7 judge `art:86b00003`, V-EX 3B/7B
  `art:d80e9eea`, rotated V-EX 7B `art:cbdc3d2a`, aw partials `art:5f893c27`.
- The FP4 keyed-transform census is `art:4bbd380a` (`note:20261001T1128Z-finding-from-e8ffd7f2-fp4-kt-census-done`). Its 3 GB of
  prepared inputs are still on node 2 under `/workspace/pouw/gpu7-fp4/kt/out/npz`, with their sha256s in the art. Free that disk when
  you want it.

## Open asks and whom they wait on

- **fb6cc95b:** bbe249577 (above).
- **f9af3acc:** a rating of the Pearl-C4 Llama-3.1-8B rows, asked in `note:20261001T1103Z-reply-from-e8ffd7f2-llama8b-timed-verified-rows-for-panel`,
  now with the 9:00 AM PDT rows too. Their M5 re-grant (`note:20261001T1514Z-reply-from-f9af3acc-m5-regrant-fp4-sm120`) covers
  n ≥ 4,096 only. Lean's `creditFp4` has no β(n), so n < 4,096 in Lean is pouw-lean's work.
- **Daniel:** landing a change to the row leaf `verity/pouw/row/v1` (compute accounting, 10:17 AM PDT).

## decode_floor.sh: approved, not launched

Compute accounting's yes (10:17 AM PDT) allows at most 0.5 GPU-h, untimed, on one node 2 GPU. Launch it after served window 4's line
leaves `fill/windows` (about 10:55 AM PDT), via `--queue` with a research question and `--custody-r2 --custody-ttl 8h`.

- It lives at `runtree/decode_floor.sh` on `cursor/pearl-c4-llama8b-window-315d`; its header has the launch line.
- The windows ran with `--project verity --campaign pouw`; the header's `--project pous` is a slip.
- `--send` needs `pearl_c4.cubin` (sha256 `dd01ae5e…`, #548's). A copy is at `/workspace/research/runs/r20261001-134930-22d2/inputs/pearl_c4.cubin`
  on node 2 (sha checked 10:20 AM PDT), and so is `IN=/workspace/pouw/fill-out/harness/inputs-bab84c16`.
- Question: how much of a decode call's 0.35–0.85 ms is A's row commitment, forming, the chain, the GEMM and the leaves, at m 64–512 on
  the four Llama-8B linears? Its milliseconds are a breakdown, never a panel number.

## r1_rows in the replay's prove: approved, not staged

`protocols/pouw/verity_pouw/schemes/pearl_c4_replay.py` on main declares only D-NF's rows in a unit's records (line 180; the shortcut
is stated at line 68). An honest prover also declares R1's rows (`PearlC4.r1_rows`, `pearl_c4.py` line 1232), so the verifier
rejects a unit when it opens an undeclared R1 row. At decode m64 most tiles are opened, which is how m64-n512-k2048 was rejected:
"B row 386 … passes R1's bound".

- The serial fix is in `art:de55903b` under `r1-reproof/r1-prove.diff`, against the run tree's copy. It calls `s.r1_rows(...)` and adds
  its rows to the record. With it, the unchanged verifier ACCEPTs that unit (max debit/cap 0.009).
- Serial, it costs about 51 µs per row-element: about 1 minute at decode and 0.5–1.7 h per prefill unit.
- Compute accounting's yes is to make it parallel and stage it as a branch for fb6cc95b. `r1_rows` splits by row: each row's term needs
  only that row and the shared basis. So chunk the rows over `prove`'s existing `_pool` fmap and add a test.

## Friction

`pouw-fp4/20261001T1714Z-friction-custody-check-from-launcher-says-no`: `research data custody RUN` run on the launching VM says
"NO custody" for every `--on` run, because the launcher's `remote.json` is never in the pod's record. Use `research data preserved RUN`
there.

## Still running

Nothing. Checked at 10:18–10:21 AM PDT:

- This VM was freshly reset, with no tmux, background shells, waiters or timers.
- I have no subscriptions and no pods (the only pod is `vy-control-verity`, not mine).
- On node 2, none of my processes, fill-queue jobs or GPU leases. My `stop_verifies.sh` watcher had exited at 9:49 AM PDT without
  acting. Its files remain in `/workspace/pouw/gpu7-fp4/l8b-window/`.
- I used no node 1 work.
- The FINAL checkpoint's finish checks never finished. On this reset VM's empty store, the custody step re-read every cited art
  from the remote, about 4.3 GB in 40 minutes. I stopped it at 11:02 AM PDT, by PID. Pods, processes and the worktree are checked by
  hand above. `art:de55903b` and `art:9bf7b791` were re-checked PRESERVED today. The other arts were PRESERVED when they were put.
