# Bench instance sets: which ref a run carries, and whether it counts in Table 2

Table 2 (`verity_numerical.bench.tables`) takes a result only if its `workload_fingerprint.instances` equals the target's
frozen ref (`tables.FROZEN_INSTANCES`: dataset, tier, range, manifest_sha256), or differs but is covered by an accepted
`instance-equiv/v1` (BRIEF §5 of morning-tables; read by tables-fix's renderer from bdaf2c44 on, and only once a
non-producer labels the file `verified=accepted`). The md render prints only the FIRST reject reason per artifact;
`--format json` has all of them (`lanes/fused-phases/evidence/pod-scripts/70-reasons.sh ART...` prints them).

## Refs at `bench-vu --total-vus 4096` (lane/fused-phases 9989797f)

| relations | ref | counts via |
|---|---|---|
| `fp8-ada`, `bf16-hopper`, `fp8-hopper` (v1) | frozen | -- |
| their `-v2 -v3 -v2x4 -v3x4 -x4` | relation-named manifest over the SAME numbers | an instance-equiv/v1 file (15, ids in `lanes/coordinator/20260924T0554Z-handoff-from-fused-phases.md`) |
| `bf16-ampere` and all its variants (A100) | frozen `vu-k1536` (bench-instances/v1) | -- ; bootstrap with `BENCH_INSTANCES=1` |
| `fp4-nvf4` (`fp4/chain.py`) | frozen NVFP4 | only at exactly `--total-vus 4096` |
| any relation with `--tile NxM` | `tileNxM` (a tile draw) | never: drill-down |

* Why derived relations differ: `relchain.instances_digest` hashes `"<relation name> synthetic|seed|n|K"`, so each variant
  names its own manifest although seed, operand recipe and model are those of v1 (a fold keeps every 4th accumulator
  public). `verity_numerical.bench.instance_equiv` (fused-phases 5b30c99b) decodes both sides with their own loaders to
  canonical x, W (operand bit words) and y (chain-end FP32 word) and compares sha256; all 15 are equal at B = 4096 and
  `--check` re-derives them at 9989797f (`lanes/fused-phases` report). A new derived relation or another `--total-vus`
  needs its own file.
* Before 5b30c99b, `bf16-ampere-v2/-v3/-v2x4/-v3x4` drew a separate synthetic set (`bench-instances-bf16-ampere/v1`, other
  numbers): results from then are drill-downs.
* Before 9989797f, `--tile` runs on fp8-ada / bf16-hopper / fp8-hopper carried the frozen ref while proving
  `relchain.tile_instances` (x, W, y all differ; `lanes/fused-phases/evidence/pod-scripts/15-tile-check.py`), e.g.
  wave-4090-2's shared committed cell art:6e2c0d79. They must not count. A committed Table 2 cell is unshared
  `--auth included-hash` on the frozen set.
* To see a relation's ref before spending pod time: `relchain.instances_ref(relations.RELATIONS[name], 4096)` (the block
  bench-vu writes; imports torch, so on a pod);
  `lanes/fused-phases/evidence/pod-scripts/10-equiv.sh` prints it for every relation next to `tables.FROZEN_INSTANCES`.
