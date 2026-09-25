---
lane: reverify-tile
kind: report
created: 2026-09-25T10:22Z
status: open
---

CHECKPOINT none (11:05Z) [open] 11:05Z: fp8-ada and bf16-hopper shared-local CPU re-productions with set.tile running on vy-reverify-tile (both benching); regression at 36%+ (1 F so far, checking). Tip f3cdfd5d pushed; focus tests 62 passed + cargo green.
CHECKPOINT 824a9924 (10:58Z) [open] tip f3cdfd5d (merged main 767115db per 1040Z handoff): cargo all ok, pytest focus 62 passed; old fa2be398/b460261f fail closed (no set.tile, unshared digest); running: rvt-regression, shipping rvt-repro-fp8-ada-2 (CPU re-production)
CHECKPOINT c06cbc9 (10:41Z) [open] 0e0d663b Rust batch refuses stmt w/o proof + test; d525c08d set.tile writer + reverify tile recompute + tile negatives; pod vy-reverify-tile (cpu3c 16vCPU) running rvt-tests-1; next: re-produce shared-local fp8-ada/bf16-hopper dumps with set.tile
CHECKPOINT a7f3f26 (10:22Z) [open] started: read contract, inbox empty; reading ligero-steps-pin report/handoff + red-team R1/R2/R4; next: design set.tile + tile_instances, create CPU pod

# reverify-tile: +shared (v6) / tile dumps re-verifiable, and Rust `batch` refuses a statement without a proof

Successor of ligero-steps-pin (FINAL, in main 3301c435). Branch `lane/reverify-tile`, worktree
`~/projects/verity-main-wt/ligero-steps-pin`, pod `vy-reverify-tile` (RunPod t32im4q69yffh6, cpu3c 16 vCPU, $0.48/h, guard 60).
Pod scripts: `evidence/pod-scripts/` (cpu_setup.sh from ligero-steps-pin, tests.sh, regression.sh, old_dumps.sh,
reproduce_shared.sh, tile_reverify.py).

## What changed (code)

- `0e0d663b` + `4afff5ae` **Rust `batch`**: a DIR holding a `*.stmt` with no `*.proof` beside it is refused, whatever the
  proofs say: `batch: N statement(s) without a proof (X.stmt, ...)`, exit 1 (precedence: unreadable files, then this, then
  sub-batch rejects, then the union bound). New test `fixture.rs::a_statement_without_a_proof_rejects_the_batch` (3 honest
  copies accepted; + an orphan stmt refused on --jobs 1 and 3 with accepted = 3; answered by a proof it accepts again).
  Behaviour change: `fixtures/fp8-ada-hash/` holds `sub_00_v6.stmt` (the same statement as v6) with no proof, so `batch
  --dir fixtures/fp8-ada-hash` is now refused; `relations.rs` asserts that and runs the pinned-batch accept on a copy of the
  proved sub-batch. No fixture changed.
- `d525c08d` **`set.tile`** and the tile recomputation:
  - `relchain.bench_vu_rel` writes, for a `--tile NXxNW` dump, `set.tile = {nx, nw, seed, draw: "relchain.tile_instances/v1",
    layout: "row-major: x = vu // nw, W = vu % nw"}` (constants `relchain.TILE_DRAW` / `TILE_LAYOUT`). `set.instances`
    was already `tile_digest` since 9989797f.
  - `reverify.tile_shape`: `set.tile` must be an object with positive integer nx, nw, nx*nw = total_vus, the bench's draw
    and layout strings, and seed = the relation's `instance_seed`; anything else is a `commitment:` FAIL.
  - `reverify.committed_trees`: with `set.tile`, the set is `relchain.tile_instances(rel, nx, nw, seed)`; `set.instances` must
    equal `tile_digest(rel, nx, nw, seed)`; the a/b/y bindings are `hashauth.binding_digest(rel.instances_dataset,
    rel.instances_tier, digest, 0, total, K, tree, schema)` (as the bench commits them); tree counts nx / nw / nx*nw; roots
    from the backend's reference builder (Poseidon2 for +shared) or core frame-v3 (keyed-BLAKE3, per-tree domain counts).
    Without `set.tile`: as before (one row per VU); a `set.sharing` label without `set.tile` is refused.
  - `reverify.commitment_problems`: a v6 dump without `set.tile` fails closed: `commitment: N row-sharing (v6) statement(s)
    and no manifest set.tile: the shared-row layout is not recomputed`; every statement's (vu, x, W) is checked against the R1
    rule (`hashauth.layout_error`: tile x = vu // nw, W = vu % nw) besides the tree equality and the cover.
  - `reverify.verify_tree`: custody covers `proof_h` (sha256), `coins_h` and `system_h_file`; `batch` gets `--system-h` when
    the manifest has `system_h_file` (before, reverify never passed it, so a pair could not have been batch-verified here).
    The verdict note says "as the NXxNW GEMM tile of the manifest's set.tile".
- `f3cdfd5d` hashauth_test: the unshared R1 forgery now gets a second (correct) problem from the layout check.
- `0c41ddf5` merge of origin/main 767115db (coordinator handoff 10:40Z; clean).
