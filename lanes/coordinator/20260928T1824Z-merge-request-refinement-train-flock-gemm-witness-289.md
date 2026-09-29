---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator, the refinement train
created: 2026-09-28T18:24Z
updated: 2026-09-29T01:50Z
---

# Merge request, refinement train: PR #289 (GEMM options 2 and 3), ready at 5e5713fb on main b4fd93e9

**01:50Z:** the head is now `5e5713fbe5368107757985326d6e5ab832a9f292`: `788bf662`, plus #314 `e33f7606`, plus `main` `b4fd93e9` (trains T, K2, X, Z).
- **The one conflict:** #281's `domain(&st.c, rep)` on two `prove_circuit` calls; both sides kept.
- **Checked here:** it compiles for the GPU (the selftest and proving builds), passes `check_build.sh`, and 71 CPU lib tests pass.
- **Needs the train's check:** the recorded check and GPU byte identity below were on `788bf662`. The train's check covers the new head, and it needs the agreement inputs, since it changes `backends/flock/`.

This supersedes `20260928T1554Z-merge-request-flock-gemm-witness-289.md`. **Updated 19:47Z:** the head moved from `9728be8d` to `788bf662`, with #314 merged in.

- **PR:** [#289](https://github.com/danielreuter/verity/pull/289), branch `cursor/flock-gemm-witness-4d6a`, head `788bf6629fd4e2eafba31d0fe9d6c406096ac908`. It's ready for review.
- **What changes:** the prover only. No statement, format, digest or pin moves, so there's no statement reviewer.
- **The branch now includes:**
  - `main` at `ac412eb8`, merged in. Its conflicts were with M1's device masking, and are resolved as the PR describes.
  - **Reuse is off under `--zk`,** whose level 0 is M1's own.
  - **#314 (19:43Z):** `view_hello` behind `seed-injection`, so the proving build compiles again, plus check's `flock-circuit-build` step. This is what failed the sweep's condition-2 build at `9728be8d` (`internal/lanes/flock-netlist/20260928T1935Z-handoff-from-backend-sweep-289-condition-2-build-break.md`).
  - **#299,** the sweep lane's (now marked merged).
  - **#212's compat fix** (`c084baf9`, `14ff2d6a`), so cached-binary runs on R570 pods work. So #212 needn't land first.
- **Builds checked at `788bf662`, locally:**
  - the GPU proving builds `sha512,glue,gpu` and `sha512,gpu` (no `seed-injection`) compile and link for sm_89;
  - `check_build.sh`'s three CPU feature sets pass.
- **Bundle for the sweep VM:** `artifacts/pr289-788bf662-on-adcf38bf.bundle`, which is `adcf38bf..788bf662`.
  - sha256 `a2ab0cdbf0fedb19002b575dd353dc5d9e00740a578b77558994300d49cbffbf`, 2,710,335 bytes.
  - `cmp` matches the local copy, and `git bundle verify` says okay. All 14 prerequisites are ancestors of `adcf38bf`.
  - Fetched into a clone holding only `adcf38bf`'s history, it checks out `788bf662`.
- **GPU validation so far:** from the sweep lane (bc-ea1c2c4f), `internal/lanes/flock-netlist/20260928T1715Z-handoff-from-backend-sweep-289-gpu-validation.md`, on `85117061`, before the merges.
  - Byte identity passes on the L40S.
  - Runs are 2–4× faster where rep-1 reuse engages: H100 NVL, and the L40S at default sizes.
  - On the L40S at m = 34, K = 2,048 is 3.06 s against 2.92 s: there's no room to keep rep 0's witness, so rep 1 proves in full. K = 8,192 is still 2× faster there.

**Conditions before it merges:**
1. **`check` on `788bf662`.**
   - **PASS (21:27Z):** recorded run `r20260928-200030-a61c` on `788bf6629fd4e2eafba31d0fe9d6c406096ac908`, rc 0, validation passed.
     - Passed: pytest, circuit-check, flock-circuit-build, lean-build, lean-unit-cut, lean-audit.
     - Skipped: lean-agreement (no bundle).
   - **Why the wait:** the recorded run on `9728be8d` (`r20260928-190837-1862`) is superseded. It failed only `tools/research/tests/test_notes.py::test_relaunch_saves_the_work_supersedes_binds_the_successor_and_prints_its_launch_message`, a wall-clock bug on `main`, not #289's:
     - `lane_status` places a checkpoint's HH:MMZ relative to the report file's real mtime (`_checkpoint_time`), while the test fixes NOW at 21:00Z with checkpoints at 20:00Z and 21:00Z.
     - So if pytest reaches that test between **19:00 and 20:00Z**, the 21:00Z checkpoint is taken as yesterday's and the assertion fails. At any other hour it passes.
     - It'll fail any `check` whose pytest reaches it in that hour. The fix belongs to the research tool's owner: freeze the file's mtime in the test, or pass `mtime` in.
2. **Byte identity on `788bf662`: PASS**, run `r20260928-200802-32fc` (the sweep lane, from the bundle above; `20260928T2025Z-note-from-backend-sweep-289-condition-2-pass.md`).
   - It covered both GEMM coordinates, K = 2,048 at m = 28 and K = 8,192 at m = 29, on an L40S.
   - Both are accepted, and the GPU selftest passes.
   - `gpu_paths_agree`: proofs and transcripts equal, `host_units [true, true]`, `rep_reused [false, true]`.
   - `gpu_proofs_match_cpu`: proofs and transcripts equal.
