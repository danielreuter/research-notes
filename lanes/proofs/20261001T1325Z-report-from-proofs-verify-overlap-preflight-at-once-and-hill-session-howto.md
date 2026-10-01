---
id: 20261001T1325Z-report-from-proofs-verify-overlap-preflight-at-once-and-hill-session-howto
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-verify-overlap (bc-96b9bb72-2593-562d-97c6-7c9f8d32b77d), re note:proofs-verify-overlap/20261001T1205Z-handoff-from-proofs-goal2-follow-through-yes
---

CHECKPOINT cc21a7d94 (13:50Z) [open] 6:51 AM PDT: owner silent; bf16-hill's ncu + K=16384 nsys in node-1 ready at 13:50Z; top-level approval posted in owner thread.
CHECKPOINT cc21a7d94 (13:49Z) [open] 6:50 AM PDT: node-1 proofs cap 7 until 14:50Z (top-level), relayed to flock-fp (note:proofs-flock-fp/20261001T1350Z).
CHECKPOINT cc21a7d94 (13:48Z) [open] 6:48 AM PDT: note:proofs/20261001T1336Z-report-from-proofs-verify-overlap-k16384-at-once-confirmed-and-rollup-arts acted on: roll-up restored (verified b1c85ac9, 11:19:31Z), arts as labels; K=16384 at once 138.7 s; label-vocab item added to morning list.
CHECKPOINT cc21a7d94 (13:33Z) [open] 6:39 AM PDT: top-level ruling (roll-up arts as labels) sent to verify-overlap (note:proofs-verify-overlap/20261001T1331Z); packed bests split from default in the bests script; NVF4 K4096 n1 packed row not keyed (note:proofs-flock-fp/20261001T1338Z); #653 carried by #655 in b27b69c1c.
CHECKPOINT cc21a7d94 (13:29Z) [open] 6:31 AM PDT: note:proofs/20261001T1325Z-report-from-proofs-verify-overlap-preflight-at-once-and-hill-session-howto acted on: yes to applying roll-up arts (own rows) and the K=16384 at-once confirmation.
CHECKPOINT cc21a7d94 (13:29Z) [open] 6:30 AM PDT: top-level approved bf16-hill's ncu + K=16384 nsys jobs; owner yes or 6:50 fallback (timer proofs-bf16-profiles-0650).
CHECKPOINT cc21a7d94 (13:28Z) [open] 6:28 AM PDT: note:proofs/20261001T1325Z-report-from-proofs-bf16-hill-k2048-nsys-profile acted on: to owner (ncu + K=16384 nsys asks) and M0 (note:flock-netlist/20261001T1328Z); s4 re-run 2.70e7, 2.61e7 holds.
# Goal 2's follow-through: the preflight's GPU cases at once at K >= 4096, and the hill-session how-to

to: proofs (bc-8416bc72). Both items are done on `cursor/proofs-verify-overlap-95d4` (head `65c230902`). I opened no PR.

## Item 2: the three GPU cases at once at K >= 4096

**Answer: against the 44, 81 and 150 s in bf16-hill's records, running the cases at once saves almost nothing.** Those
records already ran the three cases at once. bf16-hill's tree (`f12fe35`) sets `SELFTEST_JOBS=3` at every K, with no
memory guard and no per-case record. Its device-memory trace shows it: one 50.5 GB block at K=16384, which is three cases of
about 16.8 GB each, at the same time. Against running the cases one at a time, the saving is large: 102 s of 251 s at
K=16384, measured.

GPU job `r20261001-131526-f969` (tree `7d1c903`, `POINTS=0`: the check alone, 128 GiB, 6:15–6:22 AM PDT, about 6.6
GPU-minutes). It ran after the no-GPU staging job `r20261001-125609-c6a3` (5:56–6:14 AM PDT: 138, 262 and 586 s). Each K's
record, phases and dmon trace are `art:ad28516f350116821bd2b713dced5abebdb5d0b46c810cac0abdc8195afd5dae`.

| K | how the cases ran | check (s) | bf16-hill's check (s) | each case: wall s, exit, device peak MiB | sum of peaks | pod host peak |
|---|---|---|---|---|---|---|
| 4096 | at once | 43.5 | 44.1 (at once) | 17.1, 0, 5074; 17.9, 0, 4758; 17.3, 0, 4762 | 14562 MiB | 16.1 GB |
| 8192 | at once | 75.7 | 80.9 (at once) | 30.0, 0, 9272; 31.6, 0, 8652; 30.3, 0, 8658 | 26522 MiB | 27.3 GB |
| 16384 | in order (fell back) | 251.1 | 149.5 (at once) | 54.1, 0, 17678; 60.2, 0, 16440; 52.0, 0, 16448 | 17678 MiB | 28.8 GB |

The cases are listed in the order `gpu_paths_agree`, `gpu_proofs_match_cpu`, `verify_ahead_matches_serial`. Every case
passed at every K, with proofs and transcripts equal. The statement digests (`801a4254…`, `964f63d6…`, `5021e06a…`) and
proof bytes (572482, 628418, 740162 per rep) equal bf16-hill's runs. No case timed out, and the pod was never OOM-killed.

- **K=16384 fell back because my bound was wrong.** I had taken one case's device bound from the largest value in
  bf16-hill's trace (50469 MiB, so 52 GiB), assuming those cases ran one at a time. They didn't, so that value was three
  cases at once. The guard did its job: 3 × 52 GiB is more than the 95 GiB free, so the cases ran in order and still
  recorded each one's peak. **Fixed in `65c230902`:** the bounds are now each case's measured peak plus some room (6, 6, 12
  and 20 GiB at K=2048, 4096, 8192 and 16384). Three cases at K=16384 now fit (60 GiB), and bf16-hill's at-once run already
  passed with them at 52.6 GB of host memory.
- **What running at once is worth, against one at a time:**
  - measured at K=16384: 251.1 s in order against 149.5 s at once (102 s, 40%);
  - measured at K=2048: 89 s in order (`r20261001-044422-bc17`) against 26 s at once;
  - estimated at K=4096 and K=8192: about 78 s and 136 s in order (the check minus its longest case, plus the three cases'
    walls), so about 34 and 60 s saved. These are upper bounds, since a case runs slower beside two others.

## Item 1: the how-to (hill points in sessions, each citing its session's art)

- **The how-to:** a "Hill-climb points in GPU sessions" section in `backends/flock/README.md` (`7c390f8f5`, `7d1c903b5`). It
  covers staging, `POINTS=N`, and the roll-up command with its node-1 form.
- **The citing:** `gemm_hill.py rollup --attempt RUN [--run-dir DIR] --file ROLLUP` appends every point the attempt
  published. Each point carries `arts`: its own record's art (`point`), the attempt's `result.json` (`session`), and the
  check's record (`preflight`).
  - With `--run-dir`, it reads the points from the run directory and checks their sha256 against their arts. Node 1's
    store can't run `fetch`, because its index database is read-only.
  - A point already in the roll-up gets its `arts` added and is not appended twice.
  - `RESEARCH_BIN` can be a full command, which node 1 needs (`uv run ... -m research`).
  - `plot` now reads an attempt's points the same way, through `research data show`, since `select --attempt` returns
    nothing.
- **Tests:** `test_gemm_hill.py` covers the roll-up from the store and from the run directory, a tampered file, a missing
  attempt, and `POINTS=0`. Run with `test_class_statement.py` at `65c230902`: 15 passed. CPU dry runs of `POINTS=0` and
  `STAGE_ONLY=1 POINTS=0`, and of both specs' commands through the template's `bash -c`, behaved as intended.
- **Tried on real data, on a copy only:** I ran the how-to's node-1 command against a copy of
  `/workspace/usage/hillclimb/bf16-GemmCoordinate_v2-K2048.json` with my session `r20261001-092917-8b05`. All 10 of its rows
  gained `arts` (for example point 1: `art:800d2bb0…`, session `art:2298e7dc…`, preflight `art:66c9109d…`), and nothing
  else changed. Those rows now read step 13. I didn't write the shared file. Say so and I'll apply it.
- **Also on the branch:** `POINTS=0` runs the preflight check alone, and `STAGE_ONLY=1 POINTS=0` stages only its statement
  (`78009aaa5`).

## Next, if you want it

One GPU job on `65c230902` at K=16384 (`POINTS=0`, about 3 GPU-minutes, after a 10-minute no-GPU staging job on a new
tree). It would confirm the cases at once under the guard, with each case's record. Nothing is submitted. The PR waits
until after 7:50 AM PDT.
