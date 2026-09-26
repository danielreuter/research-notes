---
lane: coordinator
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T05:12Z
---

# bligero-real-k: merge-ready cursor/bligero-real-k-1521 @ 7fb9e6f6; please confirm the 16 real-K pins (non-producer) and verify art:be42c41a

**Branch:** `cursor/bligero-real-k-1521` @ 7fb9e6f6, based on origin/main 7289e3ad. It uses the cloud branch policy (not
`lane/*`). No merge conflicts are expected: the changes are additive and inside backends/direct/ligero, backends/ligero-verify
and bench.cell.

## What landed
- **Relations at vLLM's reduction lengths:** `relations._at_k` registers the x4 folds of bf16-ampere, bf16-hopper, fp8-ada and
  fp8-hopper at K = 2048 and 8192, as `<fold>-k<K>`.
  - The compiled column is the fold's own, so the bare pins are shared.
  - The statement's `steps` is K / k and is pinned per relation in Rust (`at_k!`, `Relation::vu_k` replaces
    HASHED_ROW_K in the shape check).
- **BLAKE3 leaf sized to the row:** `Blake3Leaf.for_row` handles BF16 K = 2048 (4 chunks), K = 8192 (16 chunks) and E4M3
  K = 8192 (8 chunks).
  - Each sized frame has one CV slot per chunk, the header is `n_chunks + 64 role`, and `params_sha256` carries
    max_chunks.
  - The committed bytes are unchanged (the keyed BLAKE3 of the row). The 3-chunk frame and all existing pins are
    byte-identical.
  - On the Rust side, `leaf::sized` picks the frame from the relation's row length.
- **Input sets:** `bench-vu --input-set DIR` reads the set's x/w rows (`relchain.set_instances`). The relation's model must
  reproduce every recorded output: all 6,272 and 1,920 captured instances and all 4,096 + 4,096 spine wgmma ones do, with the
  mma model.
- **B-interactive bench.cell driver:** `drivers/b_interactive.py` and `backends/direct/ligero/cell.sh`.
  - The live verifier runs on a separate pod.
  - The prover measures an open-connection ping RTT (`live probe --pings`) and bandwidth, and runs a same-run loopback
    probe at the plateau.
  - `cell.py finish/register` builds the interaction record.
- **Tests:** backends/direct/ligero real_k_test, cell_test, sweep_vu_test, blake3_test (sized frames), steps_pin_test,
  live_test (probe pings) and relations_test; bench test_cell and test_lowerings; ligero-verify `cargo test` (38 + 8 + 27).
  - Pre-existing: live_test::test_shared_pair_every_coin_from_the_verifier[None] fails when the whole file runs, on origin/main too.

## Pins: please have a non-producer confirm
- **The claim:** the PINS rows in `backends/ligero-verify/src/leaf.rs` (lane bligero-real-k block, 16 rows) are the digests
  of `system_bytes(hashchain.compose(relation("<fold>-k<K>"), leaf).sys)`.
  - The torch-free compile takes about 5 s per system on a VM CPU.
  - Check each with `ligero-verify system-digest --system <file>`.
- **Recipe:** notes `lanes/bligero-real-k/evidence/pins-vm-compile.json` (my values), and `evidence/pins-recipe.py` in the
  lane report.
- **Gadget gate:** r20260926-042639-c562 on an L40S. All 16 passed (8 honest sub-batches accepted, 86/86 negatives rejected),
  and each fixture verified pinned. Summary: notes `evidence/gates-r20260926-042639-c562.json`.

## Cells: verification requested
- **art:be42c41a:** A100 bf16-ampere-x4-k2048+blake3-xob on the captured #101 set (art:123dc234, 6,272 VUs), the set's cap.
  - 2,122 VU/s, 3.59e7x vs 312 TFLOPS; plateau sweep 1,818 / 2,036 / 2,096 / 2,122.
  - Prover run r20260926-043140-0ebf; live verifier run r20260926-041624-7d7b (still serving the next A100 cell).
  - Its run_files hold rep 1's 49 sub-batch proofs: `ligero-verify batch` with this branch's binary, or `reverify.py`,
    which now reads input-set dumps.
- **Known cell_problem:** the interaction check (my 0437Z handoff). The live transport streams proofs during proving, so the
  serial model overstates the wall by 64% at the pods' 4 Gb/s.
- **Next:** more cells follow (A100 K = 8192, H100 wgmma K = 2048 / 8192, then SHA-256). I'll hand each over as it lands.
