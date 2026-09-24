# 9989797f fill lanes can start

lane/fused-phases @ `9989797fd1d77d688a6f4236ff54c519e8ad604c` (pushed; on lane/post-wave 3adf4c28; merge-with: none).
Validation on the 4090 (seeded pre/post proof bytes, registered fp8-ada cells) is running; results go in FINAL.

## What the tip fixes

1. **Phase sum (a) -- not the fused path.** `relchain.bench_vu_rel` / `vu.bench_vu` reported the per-key *median over the reps*
   of every lap. With `--pipeline` each rep's buckets sum exactly to that rep's prover time (the pipeline rescale), but a
   median per bucket mixes reps: one or two slow timed passes make each bucket's median the largest of the fast reps, so the
   buckets exceeded the median `t.total` by 1-6.5 % (fused v3 / v3x4 are noisier and tripped; v1 p4 passed by luck). Now
   `t.total` and all six `t.*` buckets come from ONE rep, the one with the median prover time (`phases.median_rep`, as
   `fp4/chain.py` already did); `validation.evidence.phase_rep` names it, `verifier.seconds` stays a median. The prover and
   the contract check are untouched. Unit test: `backends/direct/ligero/phases_test.py` (torch-free; it also asserts that the
   old aggregation fails `contract.validate_measurements`).
2. **Instances (b), three cases.**
   - **Derived relations** (`-v2 -v3 -v2x4 -v3x4 -x4` of fp8-ada, bf16-hopper, fp8-hopper) prove the SAME numbers as v1:
     same seed, operand recipe and model, and a fold keeps every 4th accumulator public. The other manifest comes from
     `relchain.instances_digest` hashing the relation NAME (`"<rel> synthetic|seed|n|K"`). Every rejected Hopper/Ada
     manifest at B = 4096 in the store is one of these digests. All 15 are proven equal at B = 4096 by
     `verity_numerical.bench.instance_equiv` (x, W, y digests; ids below), registered unlabeled with `meta.lane =
     fused-phases`, which is the producer field tables-fix asked for. They count only once verify-night or the coordinator
     labels them and tables-fix's renderer (bdaf2c44) is in.
   - **bf16-ampere-v2 / v3 / v2x4 / v3x4 (A100)** drew a genuinely different synthetic set (`bench-instances-bf16-ampere/v1`).
     This was a runner bug, now fixed: they read the frozen `vu-k1536` set (`frozen_tier`, like `bf16-ampere` / `-x4`) and
     carry the frozen ref, so no equivalence file is needed. The gate on the frozen set passes for `bf16-ampere-v3x4` at 256
     VUs (2 honest sub-batches / 94 negatives / 0 failures); the `-v3` gate is running. Their older results stay drill-down.
   - **NEW, changes plans: `--tile` results were mislabeled frozen.** `--tile NxM` (the shared committed column,
     `--auth included-hash-shared --tile 64x64`) on fp8-ada, bf16-hopper and fp8-hopper carried the FROZEN ref while
     proving `relchain.tile_instances`, whose x, W and y all differ from the frozen set (checked on the 4090:
     `evidence/pod-scripts/15-tile-check.py`). Fixed at the tip: a tile run names its tile (`tile64x64`, `tile_digest`), so
     it is a drill-down, as bf16-ampere tile runs already were. **Existing tile results that carry a frozen ref (e.g.
     wave-4090-2's committed cell art:6e2c0d79) must not count in Table 2.** A Table-2 committed cell needs unshared
     `--auth included-hash` on the frozen set.
   - fp4-nvf4: `fp4/chain.py` already carries the frozen NVFP4 ref at `--total-vus 4096`; its rejections were B = 2048 / 4092,
     and no derived relation exists.

## Table-2-eligible from this tip

Every result still needs independent verification.

| row | `--relation` | instances | extra condition |
|---|---|---|---|
| 4090 fp8-ada-mma-draft | `fp8-ada` | frozen ref | -- |
| | `fp8-ada-v3`, `fp8-ada-v3x4` (also `-v2`, `-v2x4`, `-x4`) | equivalence file | label + tables-fix renderer |
| H100 bf16-hopper-mma-draft | `bf16-hopper` | frozen ref | -- |
| | `bf16-hopper-v3`, `-v3x4` (`-v2`, `-v2x4`, `-x4`) | equivalence file | label + tables-fix renderer |
| H100 fp8-hopper-wgmma-draft | `fp8-hopper` | frozen ref | -- |
| | `fp8-hopper-v3`, `-v3x4` (`-v2`, `-v2x4`, `-x4`) | equivalence file | label + tables-fix renderer |
| A100 first-campaign-target | `bf16-ampere`, `-x4`, `-v2`, `-v3`, `-v2x4`, `-v3x4`; `vu.py --relation bf16` | frozen ref (`vu-k1536`) | bootstrap with `BENCH_INSTANCES=1` |
| nvfp4-sm120 | `fp4-nvf4` (`fp4/chain.py`) | frozen ref at `--total-vus 4096` | -- |

## Run flags

Pod: `pod_bootstrap.sh` (`BENCH_INSTANCES=1` on the A100: the frozen arrays linked into the default `--root`), then
`source /workspace/env.sh; export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`. Fused hints are the default (no flag).

~~~
$PY -m backends.direct.ligero.run --relation REL bench-vu --zk --mode interactive --total-vus 4096 --target -128 --reps 5 \
    --batch L --pipeline P --out $D/result.json --dump-dir $D/proofs --dump-reps 1      # live: --verifier tcp://HOST:PORT
~~~

- 4090 fp8-ada (wave-4090-2's cells): `fp8-ada-v3x4 --batch 4096 --pipeline 8` (headline; p4 close), `fp8-ada-v3 --batch 16384
  --pipeline 4|8`, `fp8-ada --batch 16384 --pipeline 4`.
- H100 / A100: the same shape with `<base>-v3x4 --batch 4096` or `<base>-v3 --batch 16384`; take L / P from the device sweeps.
- Committed column: add `--auth included-hash` (unshared). Not `--tile`: tile runs are drill-downs from this tip on.
- Keep `--total-vus 4096` exactly; the refs, and so the equivalence files, are for range [0, 4096).

## instance-equiv/v1 art ids (B = 4096, all `equal: true`, unlabeled, PRESERVED)

| relation | art | relation | art |
|---|---|---|---|
| fp8-ada-v2 | art:68466c4ad6b8197ea9624fb6b50037f5338e098a1cec9bfa03c014e86eb8c3f2 | bf16-hopper-v2 | art:b5584b28cabbf0c4570c3d2554c969389461abe74f4f37b268b7f35ddfb43648 |
| fp8-ada-v3 | art:574f35193ba5abb8a5d068547e6ced872006d987ade31f65aa234c52a025743d | bf16-hopper-v3 | art:5133f6c11ad967763ccf855af7a1b16096e96eee1a1615fa2003b86396020812 |
| fp8-ada-v2x4 | art:f355573b4b2caa5ac595bb13142fa3084d364145907670827e4e3b54514eb300 | bf16-hopper-v2x4 | art:95df4a8ebc29c4a27be68933637afc620189917a0b3750990fd593683cd92850 |
| fp8-ada-v3x4 | art:d40f506558d4018603db042cb5acee0bc970669440dae1457dbce553e79a79b6 | bf16-hopper-v3x4 | art:bfd18a1dd63ce548a54dfc4ecfdf7577ee377b6a599d39dd75017e798b16347a |
| fp8-ada-x4 | art:f70cf39fef166b540e60ccc48a55fed4babd55fdfef40179c4bfaf9dff744eef | bf16-hopper-x4 | art:9c8c306ce225c2642dfe46415f36872892835ffd55ed9062d0c996f2aaddb741 |
| fp8-hopper-v2 | art:539af2c6e68ba85b1d2dd7cc2783b11cc7a9db72b8b5dc2e206a30a953a8aa64 | fp8-hopper-v3x4 | art:0749fa9dcecddd0878f753f010c87f7d3cfd43e3a356a1680a4a333acbbc35c5 |
| fp8-hopper-v3 | art:8036d0ba0d79158bf24c22522879690ceba456f5023595cc1640947886730178 | fp8-hopper-x4 | art:4cd768c2ae554be61e74874c5dca7f31bcdf0cc1a5bcb6898e0e5f2829c0dca4 |
| fp8-hopper-v2x4 | art:59193d43fe1b8b4d3fd7dc2a8be0844e014faf51170925a747821b07d78af257 | | |

The files were produced at 5b30c99b; the checker and the loaders are the same at 9989797f, which only changed the tile
refs. To reproduce them, see `lanes/verify-night/20260924T0554Z-handoff-from-fused-phases.md`.
