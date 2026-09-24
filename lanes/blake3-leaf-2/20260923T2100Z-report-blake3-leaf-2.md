---
lane: blake3-leaf-2
kind: report
created: 2026-09-23T21:00Z
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by blake3-leaf-3 (coordinator)
CHECKPOINT 1db0008 (21:10Z) — GATES 0 failures: `fp8-ada+blake3` 25 honest + 86 negatives, `bf16-hopper+blake3` 49 + 86,
`fp8-ada-x4+blake3` 13 + 86 (`--batch 2048`; at 4096 the gate's checked prove OOMs on 79 k-row columns). v2 PINS committed
(1db0008): fp8-ada 71f39e44…, bf16-hopper 58ef7097…, x4 1168788f…; the three fixture sets ACCEPT pinned in `ligero-verify batch`;
`cargo test --release` 27 + 7 + 16 = 50 passed. Fixtures on R2: art:a2e7503c… / art:78121b22… / art:51b6e9e0…; gate logs
art:02d4da16…; Rust evidence art:cb077fab…. Controls measured (4090, local coins, 4096 VUs): fp8-ada bare p4 0.172 s / p1 0.248 s /
+hash 0.568 s; bf16-hopper bare p4 0.264 s / p1 0.414 s. **The hashed runner (+hash AND +blake3) has no pipeline on any branch
(`relchain.bench_vu_rel`: `pipeline_depth = 0` when hashed): `--pipeline 4` is ignored for them.** `+blake3` at l = 8192 OOMed
(cupy Merkle buffer vs torch's cache after the checked warm-up); running l = 4096 now.
CHECKPOINT 30abee8 (20:58Z) — started. Worktree `~/projects/verity-main-wt/blake3-leaf-2` on `lane/blake3-leaf-2` @ 30abee8
(= predecessor tip; predecessor branch has no commits after 18:40Z). Pod vy-blake3-leaf (ghpl8iy5s629sq, 4090) reused, tree synced;
running: gates `fp8-ada+blake3` / `bf16-hopper+blake3` / `fp8-ada-x4+blake3` (2048 VUs, negatives, `LIGERO_GPU_STRICT=1
LIGERO_GRAPH_STRICT=1`), and on CPU: cargo build, fixtures + pins rows for the three relations, leaf tests + bf16-hopper conformance.

# Lane blake3-leaf-2 — finish the BLAKE3 leaf (re-gate, re-pin, Rust accept, `--pipeline 4` benches)

## 0. What the predecessor left (read from its report, its pod and its branch)

* Branch `lane/blake3-leaf` @ 30abee8 (on `lane/leaf-iface` 720820d): schema `blake3-keyed/row/v2`, params 6654cdb9…, role in the
  key, half-block column pairing (unfolded relations carry 32 B per operand per column: the even column parks its limbs, the odd
  column compresses; the even column's compression is computed and discarded, so x1 relations pay 2x the hash rows of the fold).
  `leaf.rs::PINS` still holds the v1 x4 pin `ac880400…` (stale).
* Found on the pod, never written up (19:00–19:06Z, logs in `/workspace/logs/`): a v2 gate of `fp8-ada-x4+blake3` (13 honest
  sub-batches, 86 negatives, 0 failures), `pytest backends/direct/ligero/leaf` 38 passed, a fixture set for
  `fp8-ada-x4+blake3` with the new pin `1168788f…` / `43e0eea0…`, and a v2 bench of `fp8-ada-x4+blake3` at l = 4096,
  `--pipeline` default: t.total 7.73 s, 79 184 rows/column, peak 14.7 GB, proof 832 MB/rep. I re-run all of it from my tree.

## Discrepancies
(none yet)

## FINAL
(pending)
