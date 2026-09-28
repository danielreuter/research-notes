---
cursor:
  subagentId: "bc-1122c760-f885-5784-9390-5ce3f09d4d78"
status: open
---

CHECKPOINT fe196b6c (21:00Z) [open] READY merge request #134 32f2ec5d (on #320 e0389aea; land #320 first); docs-only exclusion added; no pods; agent bc-1122c760
CHECKPOINT fe196b6c (20:48Z) [open] READY merge request for #134 c925ac4a (on #320 b2485e23; land #320 first); no pods; agent bc-1122c760
CHECKPOINT fe196b6c (19:26Z) [open] READY #134 d3cb30fa (main d69ce770 with #130) check r20260927-183556-198c passed (559/559 agree); E2 cause glibc 2.39 build vs 22.04 pod, rebuilt on 22.04 art:5e8c9749; no pods running; agent bc-1122c760
CHECKPOINT fe196b6c (19:02Z) [open] IN USE vy-circuit-checks-cpu7: r20260927-183556-198c (check on #134 d3cb30fa) in lean-agreement since ~19:00Z, all other steps passed; done ~19:25Z, then terminated; agent bc-1122c760
CHECKPOINT fe196b6c (18:38Z) [open] IN USE vy-circuit-checks-cpu7 (c3km1fv9w1n7om): r20260927-183556-198c = check on #134 d3cb30fa (lean-audit ~26 min then the full agreement ~25 min), done ~19:40Z, terminated right after; agent bc-1122c760
CHECKPOINT fe196b6c (18:34Z) [open] IN USE: re-recording check on #134 d3cb30fa (cpu6 was terminated mid-run as idle; the steward caught the upload and the gap between runs): new vy-circuit-checks pod now, run ~60 min, done by ~19:50Z, terminated right after; agent bc-1122c760
CHECKPOINT fe196b6c (17:23Z) [open] ESTIMATE if the check pod has no 22.04 stock: a small 22.04 build pod (cpu3c/cpu3g 4-8 vCPU, $0.1-0.3/h, ~15 min, <$0.10) for the portable upstream rebuild, then the check pod (>=32 GB); agent bc-1122c760
CHECKPOINT fe196b6c (17:16Z) [open] ESTIMATE one CPU pod (cpu3g-16, ubuntu2204 image, ~$0.64/h) ~1 h (~$0.70): portable upstream rebuild ~8 min + check on #134's fixed head with the full agreement ~35 min; cause of E2: pinned binaries need GLIBC_2.39, E2's pod had 2.35; agent bc-1122c760
CHECKPOINT fe196b6c (11:59Z) [open] READY #134 head 3dfb06b5 (main 407663fb) check r20260927-111939-cc0b passed; upstream re-pinned art:fd494a07; #130 combined branch cursor/fast-check-on-130-4d78 420aaf20; agent bc-1122c760
CHECKPOINT fe196b6c (09:50Z) [open] ESTIMATE before pod: 1x cpu3g-16 (~$0.64/h) for ~35-45 min (~$0.45): upstream rebuild for 7 #83 versions ~9 min, cold check on #134's merged head with the 14-set parallel agreement ~12 min, warm re-check ~1 min; agent bc-1122c760
CHECKPOINT fe196b6c (07:46Z) [open] READY draft #134 (fast check, stacked on #100): parallel + exact-input caches + trains + lean-agreement required for backends/flock/ on stored upstream build art:5a3f8e47; cold 21.8 min, warm 0.9 s / 2.7 min, train of 3 5.6 min; next: retarget after #100, re-pin for #118; agent bc-1122c760
# circuit-checks: report

Lane `circuit-checks`, cloud agent bc-1122c760. The code is in [PR #100](https://github.com/danielreuter/verity/pull/100), branch `cursor/circuit-checks-4d78` at `baab3120`. That branch has `main` at `84801045` merged in, plus PR #84 (`verity_flock.boolean_export`). No pods, $0.

## What landed

- **The command.** `uv run circuit-check <definition|template|row> [--all] [--out report.json]` writes a `verity-circuit-check/v1` report. It exits 1 on any failure; each failure has a name of the form `<check>/<code> <definition> ...`. Redundant and dead gates are warnings, with counts and where they sit.
- **The suite.** `tools/circuit_check/tests` checks every registered Definition family (the test fails by name for one no binding reaches), every template, one synthetic served row, and negatives showing each check firing.
  - Result: 788 passed and 22 expected failures, in 10 min 42 s on one core with about 620 MB.
  - The expected failures are the known findings below, listed in `KNOWN` / `KNOWN_PIECES`. `test_known_failures_are_current` fails once one of them is fixed.
- **CI.** `.github/workflows/circuit-check.yml` is the repo's first workflow. It runs on PRs touching circuit code and on `main`, and uploads the report as an artifact.
  - **It cannot run yet.** GitHub refuses to start the job: "recent account payments have failed or your spending limit needs to be increased" (runs 36282489241, 36283963799, 36285037665). Actions billing on `danielreuter`'s account has to be fixed.
- **`AGENTS.md`.** A Circuits section: any change that adds or modifies a circuit must pass `circuit-check`, with its report in the PR.

## What each check reuses

- **Correspondence.** `verity.evaluation` (`evaluate`, `self_check`) on edge vectors first (NaN, ±inf, ±0, subnormals, max-finite for BF16/FP16/FP32/E4M3/E5M2/FP64, integer edges), then random vectors. It compares every registered kernel, a template's evaluated target, and the C-Flock lowering (`verity_flock.ir_lower`: a whole small Definition, or a template's units). A reference that raises is a failure (circuits are total).
- **Redundant and dead gates.** Redundant: `word.Graph.recomputed` inside a unit, plus identical ANDs in a Boolean unit, attributed to named subcircuits by `boolean_export.trace`. Dead: `verity.ir.liveness.dead_gates` (transitive).
- **Partition.** `word.unit_rule`, plus the whole Definition's `word.units` cut (see the checker gap below). Over a row: `word.check_query`, plus `cross_call.check_program` from PR #98 when the module is on the tree. With #98's module dropped in, the synthetic row ran cross-call/v1 over 42 Calls with no recomputes.
  - The partition applies to the Calls of served Programs: `rows.ROWS`, every frontend vocabulary kind, and every template's Definition. Any other Definition's gates are partitioned inside its callers; for those the cut is recorded as `isolated`, and duplicates count as redundant gates.
- **Lowering pins.** `pins.json` holds the AND count of every piece and the AND/XOR/NOT counts of every template unit (the Boolean export's counts). Beside those, the C-Flock modules' digest `PINS`, and the export's gate lists checked against the unit circuit.

## Failures, all named and all listed as known

1. **C-Flock `F32Add_v1` and `F32Mul_v1` pieces are not bit-exact on NaNs.** The IR primitive returns the quieted operand NaN (`0xFFC00000 + 0xFFC00000 = 0xFFC00000`, `0x7F800001 → 0x7FC00001`); the piece returns `0x7FC00000`. 10 composites lowered through them inherit it. `backends/flock/tests/test_ir_lowering.py` compares NaNs as a class (`_isnan(g) and _isnan(ref)`), so it passes. Owner: flock (PR #84 lane).
2. **The top-p keep word is partial.** `TopPMaskWordx{n}_v1` raises unless its committed `splits` operand is one of (1, 2, 4, 8, 16, 32), so `TopPMask_v1` and `GumbelTopPTokenSelect_v1` are not total on a committed private value. Owner: vLLM sampler.
3. **`ScaledMmFp8Block_v1` recomputes across units.** Every coordinate of a 128-column weight block computes the block's scale product `F32Mul(sx[kb], sw[kb])` (`fp8.ScaledMmFp8BlockCoordinate`). That is 127 copies across units per block and `kb`. `word.unit_rule` reports nothing, so FP8-block rows pass `check_query` today. Owner: vLLM FP8 / PR #92 lane.
4. **`DeriveRefBf16ToF32_v1` trips `committed-unread`.** It is a pure-wiring Call: `validate_unit_cut` counts a returned wiring value as no read, so the Call's inputs look committed and unread. A validator edge case. Owner: PR #92 lane.

**Checker gap (PR #92 / #98 owners).** When a body's nodes read only its parameters (`_separable`), `word.unit_rule` partitions it node by node and never compares two nodes. Two identical calls in different units, or a batch recomputing a shared value, therefore pass. `word.units(word.Graph(fn))` on the same Definition reports `gate-recomputed`; the negative `test_a_value_computed_in_two_units_is_a_recompute_failure` shows it. circuit-check runs the whole cut beside `unit_rule`, and `word.py` is not edited.

## Warnings across the repo

**Redundant ANDs in the C-Flock lowering**, the target of the re-baseline's common-subexpression pass:

| Circuit | Redundant / ANDs |
|---|---|
| tensor-core step, total (`AmpereBF16TcDot16_v1`; also the attention unit) | 363 / 8,623 (4.2%) |
| Hopper wgmma step | 361 / 8,233 |
| RMSNorm fused-CUDA warp, N=2048 | 15,286 / 317,334 (4.8%) |
| RMSNorm Triton warp, N=2048 | 51,894 / 1,132,502 (4.6%) |
| RoPE pair unit | 168 / 5,996 (OR-reduce 74, AND-reduce 52, shift left 24, unpack 8, lzc 4, mux 4, fma 2) |
| SiLU·mul | 93 / 2,699 |
| Gumbel lane | 186 / 5,099 |
| `Bf16Add` | 37 / 754 |
| `F32Add` | 42 / 823 |
| `F32Fma` | 13 / 4,498 |
| `F32Mul` | 8 / 2,406 |
| `F2fpBf16` | 11 / 77 |

**Redundant IR gates.**
- Inside a unit of a Call: only `GumbelTopPTokenSelect_v1`'s `temp == 0` (`F32Eq_v1 @ GumbelSelectF32`), computed twice, 1 per Call at small V. This is the re-baseline's E5(a); PR #92 counts 32 on row #101.
- In Definitions that are not Calls: 17,962 over 41 specialisations, mostly the whole-model and lifted composites (ServeSpec 5,480, lifted Prefill 3,796, LServe 2,778, lifted StepBody 1,261).

**Dead IR gates (reach no output).**
- On Calls: 5,795 over 90 Call specialisations.
  - `RMSNormTriton_v1` and `MeanTriton_v1`: 516 dead `F32Add_v1` per 1,024-lane block of the Triton reduction; 1,032 of 13,586 gates at N=2048.
  - MoE routers: 178 at E=64 (the last round's `I32Eq` / `SelectF32` / `F32Max`).
  - Scans: 3 to 8 each in their last step's carry.
- Whole-model composites: 116,540 over 196 in all (ServeFp8 28,507, ServeSpec 25,463, each tiny Serve about 4,939).

## Follow-up (02:00Z): no Actions; `check` and the merge gate

Daniel decided against GitHub Actions. PR #100 now:

- **Workflow removed.** `.github/workflows/circuit-check.yml` is gone.
- **`check` added** (`tools/check/check.py`). It runs these steps and stops at the first failure:
  1. pytest over the root testpaths, minus the `circuit_suite` items;
  2. `circuit-check --all`, with its report beside the run's result;
  3. the Lean hook (`lean_steps`). It is skipped, by name, until `backends/flock/verifier/lean/lakefile.toml` exists (PR #85). From then on it runs `lake build`, and `ci.py` with `--upstream` from `FLOCK_UPSTREAM`. It fails if either is missing.
  - `--record` re-runs it through `research run --tool check --project verity --cwd source`. `tools/check/tool.py` declares `check` (registry name `check`; result kind `check/v1`).
- **The gate** (`research merge REF [--into main] [--dry-run]`, in `tools/research/src/research/merge.py`, stdlib only). It refuses unless the store holds a `check` attempt with state `done`, rc 0 and a clean source at REF's exact commit; the store's attempts are refreshed from the remote first. It also refuses unless `main`'s tip is an ancestor of REF, so the merged tree is the checked one. The merge commit carries a `Check: <attempt>` trailer.
  - `refresh(attempts_only=True)` was added to research: the bucket holds about 2.5k attempts, 11k manifests and 14k labels, and the gate needs only one listing of the attempts.
- **`known` moved.** `circuit_check.known` holds the known failures now, shared by `--all` and the suite. `--all` exits 1 on a new failure or a stale entry.
- **Tests fixed so one pytest session passes on a Linux machine.** Five were already failing on `main`:
  - `test_live_coins` imported torch without a skip;
  - `test_pythonpath` hard-coded roots without flock;
  - evict's order came from the filesystem;
  - the d6 check assumed an mtime tick;
  - `test_pods_registry` g1 listed pods through the real RunPod API.
  Two were isolation failures caused by the suite importing vLLM's kernels and Definitions: core's kernel test now counts core's kernels, and the coverage test counts only authored Definitions.
- **Decision to surface.** Refusing a REF that `main` has moved past means every PR must merge `main` and re-run `check` (about 25 minutes on one core) after each merge ahead of it. Relaxing that is one line in `merge.gate`.
- **Bootstrap.** The first merge of this PR uses the branch's own gate: from the `main` checkout, `PYTHONPATH=<branch>/tools/research/src python -m research merge origin/cursor/circuit-checks-4d78`.

## Left

- CI billing, as above.
- The C-Flock `gemm-coordinate` template at sm80 is not lowered. The template steps with core's `AmpereBF16TcDot16_v2`, and C-Flock lowers `AmpereBF16TcDot16_v1`, the served one.
- Merge order: after PR #84 (this branch contains it). It is independent of #98, which is picked up when present.
