---
lane: coordinator
kind: handoff
from: bench-spine
created: 2026-09-26T02:28Z
---

# bench-spine: the benchmark spine is merge-ready as PR #47 (input sets from the IR, one cell entry point, per-template lowerings)

PR [#47](https://github.com/danielreuter/verity/pull/47) is a draft, on branch `cursor/bench-spine-5777` at tip `3148fabf` (the cloud branch policy, not `lane/bench-spine`). It is based on `origin/main` 35560c88, after #39/#40. Merge it from origin.

## What it adds (all under `verity_numerical.bench`; no existing code path changes)

1. **`templates`, `input_sets` and `generate`: input sets from the IR.** They cover the seven #101 templates:
   - `gemm-coordinate` at any K, on the sm80 mma and sm90 wgmma BF16 steps;
   - FA2 `attention-head`, with T per instance;
   - `rope-head`, `rmsnorm-fused-cuda`, `rmsnorm-triton`, `silu-mul` and `gumbel-top-p-token-select`.

   Each is bound to its registered IR Definition and evaluated by `verity.evaluation`. Every subcircuit carries PR #42's exact relation, set name and ports, so captured and synthetic sets are interchangeable. Synthetic sets are `input-set/v1`: #42's layout, with the same manifest, index and provenance fields. Draws come from `verity.randomness` counter streams, and sets are prefix-stable. The store gets a new kind, `input-set/v1`.
2. **`cell plan | run | check | register`: the one benchmark entry point** for (backend, `<subcircuit>+<scheme>`, input set).
   - It plans the backend driver's `research run --on … --custody-r2 --cwd source`, with the verifier on a separate pod.
   - It checks the protocol: the contract; warm, at least 5 runs, uncontended, plateau; the interaction record; a live verifier on another host; the RTT and loopback probes; the statement and instance set.
   - It registers through the backend's own script, with the cell stamped in.
   - Drivers live in `bench/drivers/`, one module per backend. There is one today, `c_interactive`, which wraps `backends/flock/pod/30-cell.sh` (both roles) and `verity_flock.register`.
3. **`lowerings`: per-template lowering modules.** Each of A-GKR, B-Ligero, C-Flock and D-SP1 has one module per template in its own `templates/` directory. The GEMM modules map today's K=1536 cells to the relation names their scripts take. The other modules return an `n/s` reason naming the lane that will lower them.

## Tests and evidence

- **Tests:** `uv run pytest backends/numerical/tests/bench/test_input_sets.py test_lowerings.py test_cell.py`, 34 + 19 + 26 passing in about 3 s.
  - The negatives: a tampered file, a consistent manifest with a wrong output, eight protocol mutations of a real Flock cell, the prover and verifier on one host, every `n/s` path, and misnamed or missing lowering modules.
- **Full suite:** it has 9 failures and 1 collection error. All of them fail without this PR's files: the oversized `backends/ligero-verify` fixtures and `DISCREPANCIES.md`, `test_pythonpath` (it predates `backends/flock/python`), `HopperE4m3QgmmaDot32_v1` missing from `test_evaluation`'s list, no `rsync`/`torch` on the VM, and store/telemetry timing.
- **Captured sets:** all 11,040 instances of the eight captured #101 sets (`art:b5bb0ca9`) re-evaluate bit-exactly through the IR evaluator, with 0 mismatches. This was a local check on the lane VM: `lanes/bench-spine/evidence/20260926T0215Z-captured-101-verify.json`.
- **Real Flock cells:** `art:6d1295ed` and `art:d1961ba4` pass `cell.check` with no problems.
- **Synthetic sets registered and preserved** (seed 20260926), as `input-set/v1`. Digests are in `lanes/bench-spine/evidence/20260926T0225Z-suite101-local.json`.

| set | n | art |
| --- | ---: | --- |
| GEMM sm80, K = 2048 | 4,096 | `art:b88f5818` |
| GEMM sm80, K = 8192 | 4,096 | `art:b36f2c6c` |
| GEMM sm90 wgmma, K = 2048 | 4,096 | `art:4f27dc3d` |
| GEMM sm90 wgmma, K = 8192 | 4,096 | `art:ee183a74` |
| FA2 head (D = 64, BN = 128, T 1–512) | 1,024 | `art:02e8acce` |
| RoPE (D = 64) | 1,024 | `art:02a7e4df` |
| RMSNorm fused (N = 2048) | 256 | `art:09372073` |
| RMSNorm Triton (N = 2048) | 256 | `art:d8e58c81` |
| SiLU·mul (I = 8192) | 256 | `art:13e5b33b` |
| top-p (V = 128,256) | 32 | `art:ccc8afba` |

- **WAITING:** run `r20260926-021036-5fc3` on `vy-bench-spine` regenerates the same suite on a second machine (digests only). When I'm woken, I'll compare the content digests, append the result here and terminate the pod.

## Behaviour changes, and decisions for you or other lanes

- **Registration:** `register` records the lane that ran the cell as the producer (`lane`, `registered_by`), because `verity_flock.register` hardcodes `flock-backend`. The script's own values are kept under `cell.script_lane`.
- **Census (census lane):** the non-GEMM subcircuit ids (e.g. `attention-head/d64-bn128/sm80-fa2-bf16`) don't fit the `instance_sets` schema's `k[0-9]+` pattern, so the pattern needs widening before those sets can be registered. The id `sm90.wgmma.m64n8k16.bf16` isn't in `verity.ml.tc.instructions`.
- **PR #42:** its layout is matched and nothing in it needs to change. It could add `provenance.source = "captured"`; the reader infers that already. Both PRs edit `research/store/kinds.py`, in different places.
- **Drivers:** only C-interactive has one.
  - B-Ligero's `sweep_vu` records no loopback or open-connection RTT probe, and its live verifier is started over `research pods ssh`.
  - A-route-a, A-fs and D-fs have no sweep driver. Each is one new module in `bench/drivers/`.
- **Staging:** no lowering has `stage()` yet. Until one does, spine sets reach no backend; the first is the C-Flock GEMM lane at K = 2048 and 8192.
- **Recipes:** the sampler recipes are a first version: exponent windows plus basic edge words. The GEMM sums are dominated by the largest products, and there are no cancellation or floor-flush corner families yet. Changing a recipe changes the set, which is content-addressed and records its recipe.

## Pods and spend

`vy-bench-spine` is pod y8l50t1b7qhbe6, an RTX A5000 used as a CPU box at $0.27/h, because no CPU pods were available. It was created at 02:09Z and has the idle guard. It will be terminated after the regeneration run. Spend so far is under $0.20.

## Update 02:40Z: `--lane` for flock-backend's register (#34); #47 marked ready

- **New tip:** `be65eb66`.
- **The change:** `drivers/c_interactive.register()` now passes `--lane <cell lane>` to `verity_flock.register` whenever the installed script takes it. #34 (a9d13f68) makes the flag required, and `main`'s script rejects it, so either merge order works. A C-interactive cell also needs a lane at plan time now.
- **Tests:** the registration tests now run on `art:6d1295ed`'s real prover and verifier runs (fixture `tests/bench/data/flock-runs`). They pass with `main`'s `register.py` and with #34's swapped in: 30/30 each way.
- **For flock-backend:** re-registering those same runs with #34's script recomputes the coin waits and leaves the result 13% off the interaction model at its own 0.91 ms RTT (1.3 s measured, 1.5 s modelled), outside the ±10% tolerance. `cell register` refuses it, and the renderer would mark it M. With `main`'s script, the runs check clean.

## Update 02:53Z: second-machine regeneration is byte-identical; fixture on art:1589ffe1's runs; pod terminated

- **New tip:** `13b828e9` (merges `origin/main` e0dfe46f).
- **Regeneration:** run `r20260926-021036-5fc3` on `vy-bench-spine` (rc 0, preserved) regenerated the #101 suite. All 10 sets are byte-identical to the registered ones: content digest, the sha256 of every file (arrays and `index.json`) and the draw counts.
  - The two machines differ in CPU and in Python (3.14.7 on the pod, 3.12.3 on the VM; numpy 2.5.3 on both).
  - The pod ran the code from before the pool-chunking fix, so this also shows that fix leaves the output unchanged.
  - Evidence: `lanes/bench-spine/evidence/20260926T0252Z-suite101-regen-compare.json`.
- **Fixture swap:** on your note, the `art:6d1295ed` runs are superseded. The registration tests now use the runs behind `art:1589ffe1` (H100 BF16, the open-connection re-run: `r20260925-233831-a064` and `r20260925-233818-a37e`).
  - `check` is clean, and the tests pass (30/30) with `main`'s `register.py`, #34 at a9d13f68 and #34's head 4b7fb19d. The head runs `views.interaction`, which `main` has since e0dfe46f.
  - The runs' `out/` files are force-tracked, because the root `.gitignore` ignores `out/`. A fresh clone passes the tests.
- **Merge fix:** `main` renamed the census `INSTANCE_SETS` to `INPUT_SETS` (and `instance_sets.schema.json` to `input_sets.schema.json`); `bench.cell` follows it. The whole bench test directory passes: 404, with 6 skipped.
- **Provenance gap:** a synthetic set generated on a pod records `versions.git_head = null`, because `RESEARCH_SOURCE_COMMIT` isn't set there. Its `source_sha256` still pins the code.
- **Pod:** `vy-bench-spine` (y8l50t1b7qhbe6) was terminated at 02:51Z, after about 42 minutes at $0.27/h. The lane's total spend is about $0.19. Its `machines.d/vy-bench-spine.toml` entry is still there, because there's no deregister command.
