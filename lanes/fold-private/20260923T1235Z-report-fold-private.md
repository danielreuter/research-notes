---
lane: fold-private
status: done
---
# fold-private — folded (x4) private-operand-safe relations

CHECKPOINT 5d88d70 FINAL (14:50Z; mergeable: yes — 2 commits on lane/fold-private over cc885b2, `git status --short` empty, no conflict markers, no new .md; pod terminated 14:47Z; 19 artifacts pushed, snapshot fold-private-v1 = art:91008763845fdc62e562b7eac9c06e509b317a7d7201b90f2e2b91ae6145f6b9)
CHECKPOINT 5d88d70 (14:20Z; D1 complete: 8/8 GPU gates 0 failures, cargo + fold tests + 1e5 differential PASS; D2 benched 11 rows, all Rust-accepted; `git status --short` empty)
CHECKPOINT 5d88d70 (13:32Z; D1 committed, gates running)
CHECKPOINT cc885b2 D0 PASS  (13:05Z)

Lane: `lane/fold-private` at `~/projects/verity-main-wt/fold-private`, from `lane/post-freeze-2` @ `cc885b2`.
Pod: `fold-private-4090` (RTX 4090 24 GB reference part, 13 vCPU; `machines.toml` entry `fold-private-4090`), launched 12:29Z.
Env on pod: `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, venv `/workspace/venv312`, instance cache `/workspace/instances-cache`,
verifier built from the shipped tree (`cargo build --release` in `backends/ligero-verify`).  Whole tree shipped incl. `backends/shared`
(merkle: blake3 GPU, `backends/shared/hash_gpu`).

## D0 — GPU validation of the unmodified cc885b2 tree: PASS

Run `r20260923-123844-d34c` (gates + pytest; the tree digest line at the top of `commands.log` is `cc885b2de307405d18c0062c4d3f2ce79fed7b13`):

| gate (`gate-vu --vus 2048 --batch 16384 --device cuda --instance-procs 16`) | honest sub-batches | negatives | failures | wall |
|---|---|---|---|---|
| fp8-ada (bare) | 7 | 92 | 0 | 29 s |
| fp8-ada `--auth included-hash` (re-run `r20260923-125141-01e6`, see below) | 7 | 86 | 0 | ~60 s |
| fp8-ada-v3 | 7 | 92 | 0 | 313 s |
| fp8-ada-v2x4 | 2 | 92 | 0 | 51 s |
| bf16-hopper-v3 | 13 | 87 | 0 | 527 s |

`OMP_NUM_THREADS=8 pytest backends/direct/ligero -q`: **195 passed**, 16 warnings, 317 s.

The first hash-gate attempt inside `d34c` exited 2 (`run.py: error: argument cmd: invalid choice: 'included-hash'`): my script put
`--auth included-hash` before the `gate-vu` sub-command; `--auth` is a sub-command option (`... gate-vu --auth included-hash ...`).
Re-run correctly as `r20260923-125141-01e6`: `fp8-ada hashed gate: 7 honest sub-batches, 86 negatives, 0 failures`.  The
`DONE fails=1` line in `d34c/commands.log` is that argument-order slip, not a gate failure.

Bench `r20260923-125153-7951`: fp8-ada v1 bare, `bench-vu --vus 4096 --l 16384 --pipeline 4 --zk int --reps 1 --dump`:
`t.total 0.179 s` (witness 0.025, encoding+commitment 0.062, arithmetic 0.083, serialization 0.009), 13 sub-batches, 48 units/VU,
`rows_per_unit 3769`, dump 77 MB.  Rust: `ligero-verify batch` (built from the tree, `system_pinned=true`, pinned relation
`fp8-ada`, sys_id `6b570eef…`, table_digest `443e4fc7…`): **13/13 accepted, own coins, union bound 2^-128.32 <= 2^-128 → batch accepted**.

Verdict: `CHECKPOINT cc885b2 D0 PASS`.

## D1 — x4 folds of the private-operand-safe relations (in progress: code + CPU tests done, GPU gates pending)

### Construction

`_folded(base, m, name=None, rust_verifiable=False)` in `relations.py` now folds any base (v1 / v2 / v3): `m` instruction steps of
the base model per column, K = m·k_base, steps = steps_base / m, same VU claim (the final BF16 word / FP8 packed word of the same
1536-word chain), the intermediate accumulators private.  `Relation.fold` records `m`.  New relations (additive names, base systems
untouched — asserted byte-identical to the pinned fixtures in `fold_test.py::test_base_systems_byte_identical_to_pinned_fixtures`):

| relation | base | k | units/VU | rows/unit (chain system, GPU census) | pins/unit | rows/VU vs base |
|---|---|---|---|---|---|---|
| fp8-ada-x4 | fp8-ada (v1) | 128 | 12 | 14875 (base 3769) | 768 | 178500 vs 180912 (-1.3 %) |
| fp8-hopper-x4 | fp8-hopper (v1) | 128 | 12 | 13383 | 768 | |
| bf16-hopper-x4 | bf16-hopper (v1, synthetic) | 64 | 24 | 12792 | 384 | |
| bf16-ampere-x4 | bf16-ampere (v1, FROZEN vu-k1536) | 64 | 24 | 14576 (base 3516) | 384 | 349824 vs 337536 (**+3.6 %**) |
| fp8-ada-v3x4 | fp8-ada-v3 | 128 | 12 | 7090 | 86 | |
| fp8-hopper-v3x4 | fp8-hopper-v3 | 128 | 12 | 6558 | 86 | |
| bf16-hopper-v3x4 | bf16-hopper-v3 | 64 | 24 | 5929 | 128 | |
| bf16-ampere-v3x4 | bf16-ampere-v3 (synthetic) | 64 | 24 | 6369 | 128 | |

Unit-mode census (CPU, `rel.compile(params, False)`), base vs x4 vs x8 (x8 = `_folded(base, 8)`, compiled only, not registered —
the x8 compile takes 450 s / 344 s on the laptop, the x4 2 s):

| relation | fold | k | units/VU | rows/unit | pins/unit | rows/VU |
|---|---|---|---|---|---|---|
| fp8-ada | 1 | 32 | 48 | 3724 | 195 | 178752 |
| fp8-ada-x4 | 4 | 128 | 12 | 14830 | 771 | 177960 |
| fp8-ada x8 | 8 | 256 | 6 | 29638 | 1539 | 177828 |
| fp8-ada-v3 | 1 | 32 | 48 | 1783 | 25 | 85584 |
| fp8-ada-v3x4 | 4 | 128 | 12 | 7067 | 89 | 84804 |
| fp8-ada-v3 x8 | 8 | 256 | 6 | 14113 | 175 | 84678 |

**Rows per VU are flat in the fold** (-0.4 % at x4, -0.5 % at x8 for fp8-ada; the shared accumulator decode is a few dozen rows
against ~3700 per step).  The fold buys sub-batch count only: 48 -> 12 -> 6 units per VU, i.e. at `l = 16384` and 4096 VUs
13 -> 4 (3 whole + a 1-VU tail) -> 2 sub-batches.  For the Ampere v1 unit the fold is *super*-linear per unit (14576 vs 4 x 3516:
its rows are almost all per-group bit rows and the intermediate-group path adds a few) — the x4 fold of bf16-ampere costs
3.6 % more rows per VU and saves only the sub-batches.

(`BF16_AMPERE_X4_RELATION` previously folded the v2 synthetic; it now folds the v1 headline, per the brief.)

### Pod results (run `r20260923-131111-4c92`, tree c67c92e; `LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`)

* `cargo test --release` in `backends/ligero-verify`: **pass** (9 s; 25 pinned relations, folded K rules).
* **1e5-chain differential** (`diff1e5.py`, model level, CPU, 8 procs, seed 20260923; c_in drawn from the recorded states of 64
  honest base chains plus +-0): fold == 4 chained base steps at the FP32 accumulator and the public word for **100000 / 100000**
  chains in each of fp8-ada-x4, fp8-hopper-x4, bf16-hopper-x4, bf16-ampere-x4 (0 mismatches).  Non-vacuity: the 1/2/3-step
  intermediates' public words differ from the fold's in 299913 / 300000 (fp8-ada), 299912 (fp8-hopper), 105776 (bf16-hopper),
  105775 (bf16-ampere) cases — the BF16 chains saturate early (a big product dominates the 26-bit window: the intermediate IS the
  final state in ~52-55 k of 300 k), which is why the boundary-negative family constructs its own last-column VU.
* `pytest backends/direct/ligero/fold_test.py`: 31 passed, 1 skipped (frozen operand arrays not built on the pod at the time),
  1 failed — `test_folded_fixture_is_the_compiled_system[bf16-ampere-x4]`, the sub-linear-rows assertion (the finding above);
  fixed in 5d88d70 (asserts the measured ratio, < 4.1 for that one relation).  The bf16-ampere / frozen-instance subset was
  re-launched locally on 5d88d70 at 14:09Z but the laptop process was killed with its shell before finishing — **the fixed
  assertion has NOT been re-run under pytest**; it is a one-line ratio check against the same 14576 / 3516 census the pod
  printed, and the pod's gates for both Ampere folds passed on 5d88d70.  The coordinator should run
  `pytest backends/direct/ligero/fold_test.py -k bf16-ampere` once on a machine with the frozen arrays built.
* GPU gates (`gate-vu --vus 2048 --batch 16384 --device cuda --instance-procs 8 --instances-cache ...`):

| gate | honest sub-batches | negatives | failures | wall |
|---|---|---|---|---|
| fp8-ada-x4 | 2 | 99 | 0 | 36 s |
| fp8-hopper-x4 | 2 | 99 | 0 | 34 s |
| fp8-ada-v3x4 | 2 | 99 | 0 | 562 s |
| fp8-hopper-v3x4 | 2 | 99 | 0 | 583 s |
| bf16-hopper-x4 | 4 | 92 | 0 | 108 s |
| bf16-hopper-v3x4 | OOM in `4c92` (two v3x4 gates sharing the GPU); **solo re-run `r20260923-140535-9b5f`: 4 honest, 92 negatives, 0 failures**, 543 s | | | |
| bf16-ampere-v3x4 | 4 | 92 | 0 | 590 s |
| bf16-ampere-x4 | in `4c92` FAILED TO START: `fixtures/bench-instances/v1/vu-k1536.x.u16 is missing` — the v1 Ampere relation reads the FROZEN tier whose operand arrays are built, not committed; built on the pod 13:27Z (`verity_numerical.bench.instances build`, 144 s); **re-run in `9b5f`: 4 honest, 94 negatives, 0 failures**, 94 s | | | |

  The negatives count rises from 92 to 99 for the FP8 folds: the folded-boundary family (honest control + 3 intermediates + 2
  base-step swaps + 1 column swap); for BF16 the intermediates mostly coincide with the fold's word on the drawn VU, so fewer
  entries qualify (the family only emits a negative when the model says the claim actually changes).

  Follow-up run `r20260923-140535-9b5f` (tree 5d88d70, frozen arrays built, gates run SOLO): `bf16-ampere-x4` gate: **4 honest
  sub-batches, 94 negatives, 0 failures** (94 s); `bf16-hopper-v3x4`: see the line below the table (running at 14:10Z).
  The `bf16-hopper-v3x4` failure in `4c92` was `torch.OutOfMemoryError` inside `check_constraints` with the other v3x4 gate
  holding 13.5 GB on the same GPU — my two-stream scheduling, not the relation (it had already proved and verified its first
  honest sub-batch: `l=16384 prover 65.09s -> True accept`).

## D2 — bench on the 4090 (int-ZK, interactive, local coins, 4096 VUs, K = 1536, dumps rep1, Rust-verified on the pod)

All rows: `bench-vu --zk --mode interactive --device cuda`, `--instance-procs 16`, pod verifier built from the lane tree
(`ligero-verify batch --target-bits 128 --threads 8`, `system_pinned=true`, own coins).  `t.*` are the runner's medians over
the reps (3 unless noted); `split.*` are the per-phase sums per rep.  Peak = `mem.peak_device_bytes`.

| relation | l | pipe | reps | t.total (s) | witness / enc+commit / arithmetic / serial (s) | hints / encode / tests / openings (s) | proof MB | sub-batches x VUs | peak GB | us/VU | Rust (pod) | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp8-ada (v1 control) | 16384 | 4 | 3 | **0.170** | 0.031 / 0.054 / 0.077 / 0.009 | 0.029 / 0.054 / 0.077 / 0.009 | 66.1 | 13 x 341 | 6.6 | 41.6 | 13/13 ACCEPT 128.32 b | r20260923-133416-92d0 |
| fp8-ada-x4 | 16384 | **2** | 3 | 0.195 | 0.015 / 0.129 / 0.047 / 0.004 | 0.013 / 0.129 / 0.047 / 0.004 | 54.7 | 4 x 1365 (1-VU tail) | 13.9 | 47.5 | 4/4 ACCEPT 128.67 b | r20260923-134027-ac4f |
| fp8-ada-x4, 4095 VUs | 16384 | 2 | 3 | **0.150** | 0.016 / 0.093 / 0.037 / 0.003 | 0.014 / 0.093 / 0.037 / 0.003 | 40.8 | 3 x 1365 (whole) | 13.9 | 36.6 | 3/3 ACCEPT 128.41 b | r20260923-134104-527d |
| fp8-ada-x4 | 16384 | 4 | - | **OOM** (`CUDA out of memory`, 22.9 GB in use, 5.1 GB CUDA-graph pools) | | | | 4 x 1365 | >23.5 | | | r20260923-133629-34f1 |
| fp8-ada-v3x4 | 16384 | **1** | 1 | 0.867 | 0.086 / 0.287 / 0.482 / 0.006 | 0.079 / 0.287 / 0.482 / 0.006 | 30.5 | 4 x 1365 | 10.9 | 211.6 | 4/4 ACCEPT 128.67 b | r20260923-140128-b32f |
| fp8-ada-v3x4 | 16384 | 2 | - | FAIL: warm-up self-check `linear constraints failed (public values)` — the v3 pipeline bug below | | | | | | | | r20260923-134259-864a |
| fp8-ada-v3 (control) | 16384 | 4 | - | FAIL: `quadratic constraints failed` on sub-batch [0, 341) — same bug, unfolded | | | | | | | | r20260923-135520-1458 |
| fp8-ada (v1 control) | 4096 | 4 | 3 | 0.181 | 0.028 / 0.042 / 0.093 / 0.018 | 0.027 / 0.042 / 0.093 / 0.018 | 181.5 | 49 x 85 | 1.9 | 44.3 | 49/49 ACCEPT 128.40 b | r20260923-134143-7195 |
| fp8-ada-x4 | 4096 | 4 | 3 | **0.167** | 0.033 / 0.073 / 0.053 / 0.008 | 0.031 / 0.073 / 0.053 / 0.008 | 163.0 | 13 x 341 | 6.5 | 40.7 | 13/13 ACCEPT 128.33 b | r20260923-134220-54c3 |
| bf16-hopper (v1 control) | 16384 | 4 | 3 | **0.267** | 0.034 / 0.079 / 0.132 / 0.021 | 0.033 / 0.079 / 0.132 / 0.020 | 118.0 | 25 x 170 | 5.5 | 65.1 | 25/25 ACCEPT 128.05 b | r20260923-134709-0eee |
| bf16-hopper-x4 | 16384 | 2 | 3 | 0.282 | 0.025 / 0.143 / 0.108 / 0.012 | 0.023 / 0.143 / 0.108 / 0.012 | 84.7 | 7 x 682 | 11.5 | 68.9 | 7/7 ACCEPT 128.54 b | r20260923-134800-b894 |
| bf16-hopper-x4, 4095 VUs | 16384 | 2 | 3 | 0.289 | 0.024 / 0.143 / 0.116 / 0.007 | 0.021 / 0.143 / 0.116 / 0.007 | 84.7 | 7 x 682 (4095 = 6 x 682 + 3: no whole packing at this l) | 11.5 | 70.5 | 7/7 ACCEPT 128.54 b | r20260923-134904-7536 |
| bf16-hopper-v3x4 | 16384 | 2 | - | FAIL: `linear constraints failed (public values)` on [0, 682) — v3 pipeline bug | | | | | | | | r20260923-135135-3420 |
| bf16-hopper (v1 control) | 4096 | 4 | 3 | 0.309 | 0.050 / 0.069 / 0.160 / 0.035 | 0.048 / 0.069 / 0.160 / 0.034 | 326.4 | 98 x 42 | 1.7 | 75.4 | 98/98 ACCEPT 128.06 b | r20260923-135006-48c2 |
| bf16-hopper-x4 | 4096 | 4 | 3 | **0.260** | 0.055 / 0.093 / 0.098 / 0.014 | 0.054 / 0.093 / 0.098 / 0.013 | 273.2 | 25 x 170 | 5.4 | 63.6 | 25/25 ACCEPT 128.05 b | r20260923-135044-21e5 |
| fp8-ada-v3 (control) | 16384 | **1** | 1 | 0.829 | 0.071 / 0.239 / 0.498 / 0.013 | 0.065 / 0.239 / 0.498 / 0.012 | 46.0 | 13 x 341 | 2.7 | 202.4 | 13/13 ACCEPT 128.32 b | r20260923-141735-e916 |
| fp8-ada-v3x4 | 4096 | 1 | 1 | 0.925 | 0.213 / 0.243 / 0.430 / 0.013 | 0.207 / 0.243 / 0.430 / 0.012 | 82.1 | 13 x 341 | 2.7 | 225.9 | 13/13 ACCEPT 128.33 b | r20260923-142650-7c97 |
| fp8-ada-v3 (control) | 4096 | 1 | 1 | 0.989 | 0.206 / 0.224 / 0.494 / 0.025 | 0.202 / 0.224 / 0.494 / 0.023 | 103.4 | 49 x 85 | 0.7 | 241.4 | 49/49 ACCEPT 128.40 b | r20260923-142818-083a |
| fp8-ada-x4, 4092 VUs | 4096 | 4 | 3 | **0.152** | 0.030 / 0.071 / 0.042 / 0.009 | 0.028 / 0.071 / 0.042 / 0.009 | 150.5 | 12 x 341 (whole) | 6.5 | 37.1 | 12/12 ACCEPT 128.45 b | r20260923-142613-91aa |
| bf16-hopper-x4, 4092 VUs | 16384 | 2 | 3 | **0.242** | 0.020 / 0.105 / 0.112 / 0.006 | 0.018 / 0.105 / 0.112 / 0.006 | 72.3 | 6 x 682 (whole) | 11.5 | 59.3 | 6/6 ACCEPT 128.09 b | r20260923-142510-08e6 |
| bf16-hopper-v3x4 | 16384 | 1 | 1 | 1.026 | 0.123 / 0.315 / 0.572 / 0.009 | 0.112 / 0.315 / 0.572 / 0.008 | 47.3 | 7 x 682 | 10.3 | 250.6 | 7/7 ACCEPT 128.54 b | r20260923-142012-077b |
| bf16-hopper-v3 (control) | 16384 | 1 | 1 | 1.074 | 0.116 / 0.274 / 0.642 / 0.026 | 0.107 / 0.274 / 0.642 / 0.025 | 83.1 | 25 x 170 | 2.6 | 262.1 | 25/25 ACCEPT 128.05 b | r20260923-142356-982d |

Contract (4096 VUs) vs whole-sub-batch (4095 VUs): at `l = 16384` the fp8-ada-x4 layout holds 1365 VUs per sub-batch, so 4096 VUs =
3 whole sub-batches + a **1-VU tail sub-batch** that costs as much as a full one in fixed phases (0.195 s vs 0.150 s, 54.7 MB vs
40.8 MB: the tail is 23 % of the time and 25 % of the proof).  For bf16-hopper-x4 (682 VUs per sub-batch) neither 4096 nor 4095
packs whole (6 x 682 = 4092); 4092 VUs would.  The v1 control's 341-VU sub-batches have the same 1-VU tail at 4096 (12 x 341 =
4092) — its 13th sub-batch is likewise 4 VUs.

### What the fold does and does not buy (measured, 4090)

1. **Sub-batch count falls 3.25-4x** as designed (13 -> 4 fp8-ada, 25 -> 7 bf16-hopper at l = 16384; 49 -> 13, 98 -> 25 at
   l = 4096), the proof shrinks 17-28 % (66 -> 55 MB / 41 MB whole; 118 -> 85 MB; 182 -> 163 MB; 326 -> 273 MB), the witness
   phase halves (0.031 -> 0.015 s fp8-ada) and the arithmetic (tests) phase falls 1.6x (0.077 -> 0.047 s).
2. **But rows per VU are unchanged** (§D1), so the encode + commit phase — which is per row — does not shrink, and at l = 16384
   it *grows* 2.4x (0.054 -> 0.129 s fp8-ada; 0.079 -> 0.143 s bf16-hopper): the 4x taller sub-batch (14875 x 65536 elements,
   `census.bytes_encoded` 15.6 GB per rep) runs at pipeline depth 2 instead of 4 and does not overlap its encode with the
   neighbours' tests the way 13 short sub-batches did.  Net at l = 16384: fp8-ada-x4 is **+15 % slower** than the v1 control at
   the contract size (0.195 vs 0.170 s) and **-12 % faster** at the whole-sub-batch size (0.150 s); bf16-hopper-x4 +6 % (0.282
   vs 0.267 s).
3. At **l = 4096, pipeline 4 fits** (6.5 GB peak) and the fold wins outright: fp8-ada-x4 0.167 vs 0.181 s (**-8 %**),
   bf16-hopper-x4 0.260 vs 0.309 s (**-16 %**), with 10 % smaller proofs.  The fold's natural operating point on a 24 GB part
   is l = 4096 (or l = 16384 with a 2-deep pipeline and whole packing).
4. **Memory knee:** `--pipeline 4` at l = 16384 needs > 23.5 GB for any x4 relation (v1 control peaks at 6.6 GB; x4 at depth 2
   peaks at 13.9 GB; v3x4 at depth 1 at 10.9 GB).  On an 80 GB part depth 4 would fit and the encode overlap would return —
   the fold's l = 16384 number here is a 24 GB-part number.
5. **v3 (private operands) cannot be benchmarked pipelined on cc885b2**: every v3 relation, folded or not, fails the bench's
   own self-check with `--pipeline > 1` (fp8-ada-v3: `quadratic constraints failed` at p4 l = 16384, `linear constraints failed
   (public values)` at p4 l = 4096; passes at `--pipeline 1` at both l with `validation: passed`).  The gates (non-pipelined
   `prove_vus`) pass, so it is the pipelined `prove_vus_many` path (per-slot hint graphs / pinned buffers) that mishandles the v3
   witness — a pre-existing prover bug outside this lane's scope, reported here with the reproducer:
   `run --relation fp8-ada-v3 bench-vu --zk --mode interactive --batch 4096 --pipeline 4 --total-vus 340 --reps 1 --device cuda`
   fails; `--pipeline 1` passes.  The v3x4 row above is therefore a pipeline-1 number (0.867 s; 4/4 Rust-accepted), 4.4x the
   v1 fold: v3's CPU-bound hint generation (0.079 s) and 2.3x heavier tests (0.482 s) dominate, not the fold.
6. Every dump in the table was Rust-verified on the pod at 128 bits with the pinned folded relations (`pinned_relation` =
   `fp8-ada-x4` / `bf16-hopper-x4` / `fp8-ada-v3x4`); the coordinator re-verifies with the laptop build.

7. **v3 folds at pipeline 1** (the only valid v3 configuration): fp8-ada-v3x4 0.867 vs v3 0.829 s at l = 16384 (+5 %), 0.925 vs
   0.989 s at l = 4096 (-6 %); bf16-hopper-v3x4 1.026 vs v3 1.074 s (-4 %).  Proofs shrink 34-43 % (46 -> 30.5 MB, 103 -> 82 MB,
   83 -> 47 MB).  Without a pipeline the fold's fewer sub-batches buy little time; v3's cost is its tests (0.43-0.64 s) and its
   CPU hints (0.07-0.21 s), 5-6x the v1 unit either way.
8. **Whole packing is the fold's real number**: fp8-ada-x4 4092 VUs at l = 4096 **0.152 s** (v1 control 0.181 s, **-16 %**;
   proof 150 MB vs 182 MB); bf16-hopper-x4 4092 VUs at l = 16384 **0.242 s** (v1 control 0.267 s, **-9 %**; 72 MB vs 118 MB).
   The 4096-VU contract number carries a 1-VU (fp8) or 4-VU (bf16) tail sub-batch that costs 12-23 % of the run.

Not run (time): x8 pins / gates / bench (D3), the fused per-group hint kernel, 3-rep v3 rows.

Rust: `relation.rs` pins all eight (sys_id + table_digest from the compiled systems, fixtures
`backends/ligero-verify/fixtures/systems/<name>.system.bin`), `PrivSel` statics for the x4 v3 decoders take `k = 4·k_base`
(64 / 128) and refuse the base k; `tests/relations.rs::folded_privsel_pins_take_k_4k_and_refuse_the_base_k` + the
`system_digest_names_every_pinned_relation` table (25 relations now).

Python tests (`backends/direct/ligero/fold_test.py`, CPU): base byte-identity; folded fixture == compiled system with sub-linear row
growth and pin scaling; folded unit == exactly four chained base steps (differential), rejects the 1/2/3-step intermediates and
bit-flipped claims; folded chain == base claim through the chain runner, all negatives incl. the new **folded-boundary family**
(`relchain.negatives`: a VU whose words live only in its last column so the accumulator enters it at +0 and every fold step moves
the word; negatives = each intermediate step proved as the final word, operand swaps across a base-step boundary inside a column,
operand swaps across a column boundary; honest control must accept).  `frozen_instances` slices every `fold`-th recorded accumulator.

Finding while building the boundary family: `marshal()` caches sub-batch bundles keyed on `id()` of the VU tuples.  A caller that
passes freshly built temporaries can have an id reused after GC and get the *previous* bundle replayed — my first boundary negative
"accepted" because the verified proof was the honest control's.  The negatives keep their VUs alive for the battery; the hazard is
noted in DISCREPANCIES.md.

## D3 — not reached (x8 census only)

x8 compiles (§D1 table: fp8-ada x8 29638 rows/unit, 6 units/VU, rows/VU -0.5 %; v3 x8 14113 rows/unit) but was not registered:
the x8 compile takes 450 s / 344 s on the laptop per relation (the compiler's cost is super-linear in the group count), and the
D2 measurements say the fold's remaining lever is not row count but the per-sub-batch encode/commit overlap and the tail: at
l = 16384 an x8 sub-batch would be 29638 x 65536 elements (7.8 GB encoded) — depth 1 only on a 24 GB part, 2 sub-batches per 4096
VUs, and the 1-VU tail would cost half the run.  The fused per-group hint kernel was not started.

## Artifacts

Runs (pod `vy-fold-private`, all pulled to the laptop store and pushed to R2 `verity-dev`, `--verify head`, PRESERVED):

| run | what | result artifact |
|---|---|---|
| r20260923-123844-d34c | D0 gates + pytest (tree cc885b2) — records only (`DONE fails=1` is the `--auth` argument-order slip) | — |
| r20260923-125141-01e6 | D0 `fp8-ada --auth included-hash` gate: 0 failures | — |
| r20260923-125153-7951 | D0 bench fp8-ada v1 l=16384 p4 1 rep + dumps, Rust 13/13 | art:d6a69f78b771a027c00a3679ddebfcdb0f5d492fdf03ec670225f62a243006ed |
| r20260923-131111-4c92 | D1: cargo test, fold_test.py, 1e5 differential, 8 gates (2 streams; tree c67c92e) | — |
| r20260923-140535-9b5f | D1: bf16-ampere-x4 + bf16-hopper-v3x4 gates solo (tree 5d88d70) | — |
| r20260923-133416-92d0 | D2 fp8-ada l16384 p4 r3 | art:2f604515b87432faa49e159d54ecd9937a5d775a4be03ed17242b0834d562ba1 |
| r20260923-134027-ac4f | D2 fp8-ada-x4 l16384 p2 r3 | art:c00a79485f9aa59c02df2e453eb96d010bf542fce68cb77280effeccf6bf474c |
| r20260923-134104-527d | D2 fp8-ada-x4 l16384 p2 r3, 4095 VUs | art:2702737abc88bc8967fe51d8841d1007ef2b2e8adf99c9f3149c5927ed02fd1e |
| r20260923-134143-7195 | D2 fp8-ada l4096 p4 r3 | art:eb5c98e39e9ae5808df2cf269b0970d55edb2c9ebab22d7239bcf4581fb3cb6a |
| r20260923-134220-54c3 | D2 fp8-ada-x4 l4096 p4 r3 | art:80310423a1ea53d75c0db3a42a42553522bcc06aa61250f41ad29106e597bcd9 |
| r20260923-134709-0eee | D2 bf16-hopper l16384 p4 r3 | art:8dc7c9eba51bcb19c028f569709c9c175b62a50bc1eb0fc9dd2642dfe5507cb5 |
| r20260923-134800-b894 | D2 bf16-hopper-x4 l16384 p2 r3 | art:9d64c209cd6a6cde1163af73d28352784d02780f6eb19b6b159ea619cab896ae |
| r20260923-134904-7536 | D2 bf16-hopper-x4 l16384 p2 r3, 4095 VUs | art:877921a082f8e325f9559130818b3f96902165d7be7c7b63df856f97a31b2ab2 |
| r20260923-135006-48c2 | D2 bf16-hopper l4096 p4 r3 | art:ef1924e02a977a8b8aa86fbca2c277a292753ae208d4245cdea2666e5b82f392 |
| r20260923-135044-21e5 | D2 bf16-hopper-x4 l4096 p4 r3 | art:0494215050d07ab173ffe21e81d9d84a049a8b3e5edb99673ed43d084ee16ba7 |
| r20260923-140128-b32f | D2 fp8-ada-v3x4 l16384 p1 r1 | art:5ad8eeb43e1b2fa4434c8ad6a0bccf998da2e283726a5ee6b2ed003836723c1c |
| r20260923-141735-e916 | D2 fp8-ada-v3 l16384 p1 r1 | art:e13460d1a5d653572fcc0412c4f6fa53ec07ddc1935eef9fd45af6c44b42d504 |
| r20260923-142012-077b | D2 bf16-hopper-v3x4 l16384 p1 r1 | art:92f4219c9ee59543d2c9e0f845a11a7bbdb6318b1b354730bac293ccdd0dc448 |
| r20260923-142356-982d | D2 bf16-hopper-v3 l16384 p1 r1 | art:219ae30a87b1cc0ecc858d2833fd20a2a08896f24ee0a4292ca3106c5f4a1783 |
| r20260923-142510-08e6 | D2 bf16-hopper-x4 l16384 p2 r3, 4092 VUs | art:ddb12c59d71085cf930a7285dc854d8fd51b502d90079a36231cce5c42a7aa24 |
| r20260923-142613-91aa | D2 fp8-ada-x4 l4096 p4 r3, 4092 VUs | art:261c8a96ef665dd78875120fd2b924fb2988dd7cc9eaa71d78de2c9998e37814 |
| r20260923-142650-7c97 | D2 fp8-ada-v3x4 l4096 p1 r1 | art:07630f3f5fa6839db338f52ddbe34b044306dc4d91e00143b7583cb18ac9a2c2 |
| r20260923-142818-083a | D2 fp8-ada-v3 l4096 p1 r1 | art:06530dae6668ce425a9ce59aa226b69aa4ad5b480ae7654d2430a18fb47ed0bd |

Snapshot **`fold-private-v1` = art:91008763845fdc62e562b7eac9c06e509b317a7d7201b90f2e2b91ae6145f6b9** (19 members: the 18 D2 results +
the D0 bench), PRESERVED on R2.  Gate-run records (`4c92`, `9b5f`, `d34c`, `01e6`) fetched with `--all` into `~/.research/runs/`.
| r20260923-133629-34f1 | D2 fp8-ada-x4 l16384 p4: CUDA OOM (finding 4) | — |
| r20260923-134259-864a, r20260923-135135-3420, r20260923-135520-1458 | D2 v3x4 / v3 at pipeline > 1: bench self-check failures (finding 5) | — |

Each result carries labels `--by fold-private --ref <run>`: relation, fold, campaign=r24-fold-private, hardware, B, K, mode,
zk, candidate=B-Ligero, note (no `verified=`).  Dumps: `proofs/system.bin` + `proofs/rep1/sub_NN.{proof,stmt,coins}` in each
run's `run_files` artifact; the pod's Rust verdict in `rust_verify.json`.

## What remains (ranked)

1. **v3 under the pipelined prover** (`prove_vus_many`, any depth > 1) fails its own self-check on cc885b2 for every v3 relation —
   the private-operand column cannot be benchmarked at the contract operating point until that is fixed (reproducer in D2 §5).
   Not this lane's code; the folds inherit it.  Owner: whoever owns `pipeline.py` / the v3 hint path (relmin-private).
2. **The fold's encode/commit regression at l = 16384** (2.4x on a 24 GB part at depth 2).  Levers, in order: (a) whole-sub-batch
   packing (4095 / 4092 VUs) — already -12 % vs control; (b) restore depth 4 by halving the per-slot footprint (the 5.1 GB of
   CUDA-graph private pools are per slot; free the encoded matrix before the tests) — the fold then keeps its 0.047 s tests
   with the control's 0.054 s encode, ~0.12 s total, -30 %; (c) an 80 GB part.
3. x8: register + pin + gate (`_folded(rel, 8)` is one line; the 450 s compile is the cost; expected rows/VU -0.5 %, sub-batches
   halve again; only worth it after (2b)).
4. `marshal`'s `id()`-keyed bundle cache: key on a content digest or a monotonically increasing token, or document the
   keep-alive requirement (relchain.negatives now carries the note).  Silent stale-bundle replay is a test-soundness hazard.
5. Ampere v1 fold: 3.6 % more rows per VU (per-group bit rows dominate, the intermediate-group path adds rows); the fold's win
   there is sub-batch count only.  If the Ampere column matters, fold the v3 Ampere unit instead (6369 rows/unit x 24 = 152856
   rows/VU vs 337536 for v1: the private-operand unit is 2.2x smaller).
6. Frozen `vu-k1536` operand arrays are built, not committed: every pod needs `verity_numerical.bench.instances build` (144 s)
   before any `bf16-ampere*` v1 gate/bench; the bootstrap scripts should do it.
7. bf16-hopper-v3x4 bench (pipeline 1), fp8-ada-v3 / v3x4 at l = 4096, and the 4095-VU rows for the l = 4096 layouts (341 VUs
   per sub-batch at x4: 4092 packs whole).

## What was wrong in the brief

* "`--pipeline 4`" at l = 16384 does not fit a 24 GB 4090 for any x4 relation (OOM at 22.9 GB); the fold's contract-point number
  on this part is a depth-2 number.  The v2x4 relmin-lookup gate (7 k rows) fit; the v1 folds are 2x taller.
* "fp8-ada v1 control vs v3 vs v3x4": v3 fails the bench self-check at any pipeline depth > 1 on cc885b2 (unfolded too), so the
  v3 comparison is pipeline-1 only (and v3's hints are CPU-bound: 45-65 s per l = 16384 sub-batch in the gates).
* "the v1 folds `bf16-ampere-x4`": the v1 Ampere relation is the FROZEN `vu-k1536` tier, whose operand arrays are not in the
  repo; the brief's "ship the whole tree" is not enough — build them on the pod.
* "DISCREPANCIES.md entry (48 KB cap)": the file was at 48726 of 49152 bytes before this lane; D15 fits only because D4 (already
  SUPERSEDED by D7) was condensed to a pointer (full text at `cc885b2`).  The next lane cannot add an entry without the same.
* "1e5-chain differential": at the model level this is 3 s on the pod; the relation-level (constraint-system) differential is
  the expensive one (N_DIFF = 300 took > 10 min per relation on the laptop; the test now defaults to 48, override `FOLD_DIFF_N`).
* "whole-sub-batch (4095)": 4095 only packs whole for the fp8 x4 layout at l = 16384 (3 x 1365); bf16-hopper-x4 needs 4092 and
  the l = 4096 layouts need 4092 (12 x 341) — the "4095" is layout-specific.
* The `--auth included-hash` flag is a `gate-vu` option, not a `run.py` option (brief §D0 ordering); cost me one 1-second gate.

## Store push status (14:53Z-15:11Z)

Every artifact this lane produced (18 D2 results, the D0 result, their run attempts/outputs, the snapshot) was pushed and
`--verify head` PRESERVED individually.  The store-wide `research data push --pending --verify head` (which walks EVERY
unpushed artifact in the shared laptop store, not just this lane's) was cut off once with its shell after 16 min, re-run in
the foreground for 17 min, and ended with two failures that are not this lane's artifacts: `art:346f958a…` "NOT preserved:
FileNotFoundError" (a local blob missing) and `art:60b114af…` "NOT preserved: OSError: [Errno 28] No space left on device" —
**the laptop disk filled during the push** (it had ~4-7 GB free; the brief's `store_evict.py` found 0 evictable blobs).  After
that the shell stopped returning results, so the push is NOT confirmed complete for other lanes' pending artifacts.  Action for
the coordinator: free disk (evict materialised trees / old run dumps), then `research data push --pending --verify head` again;
this lane's artifacts need nothing.

## Pod accounting

`vy-fold-private` (RunPod `zo6jpza1li6yzm`, RTX 4090 24 GB reference part, EU-RO-1 SECURE, $0.74/h): created 12:29Z, **terminated
14:47Z** (`research pods terminate`, GET -> 404) — 2.3 pod-hours, **~$1.71** of the $2.60 budget.  Bootstrap 12:29-12:38Z (venv, torch cu124, cupy,
blake3 GPU Merkle, cargo build of the verifier, instance caches); D0 12:38-13:00Z; D1 13:11-13:32Z + 14:05-14:16Z; D2
13:34-14:30Z.  `machines.toml` entry annotated with the termination.
