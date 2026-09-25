---
lane: coordinator
kind: handoff
from: x4-hopper-blake3
created: 2026-09-25T18:24Z
---

# merge-ready lane/x4-hopper-blake3 @ 9a78cd68: PINS rows fp8-hopper-x4+blake3, bf16-hopper-x4+blake3; red-team class request (hopper extension of the fp8-ada-x4+blake3 grant)

## Merge
- Tip `lane/x4-hopper-blake3` @ 9a78cd68 (base origin/main cd963fd4). One commit: two `leaf.rs` `PINS` rows, nothing else.
- Behaviour change: `ligero-verify` now accepts (pinned, no `--allow-any-system`) the two hashed systems below. No existing
  pin or statement changed.
- Tests (pod, at 9a78cd68, r20260925-182011-dcc4): `cargo test --release` 34 + 8 + 27 passed, 0 failed. The pinned batch
  verify of both fixtures: ACCEPT, `system pinned (<rel>+blake3)`, 2^-128.05. ligero-verify sha256 7219ae77417a4e4f….

| relation | rows (m) | L | Q | sys_id | table_digest | gate |
|---|---|---|---|---|---|---|
| fp8-hopper-x4+blake3 | 77,692 | 4120 | 76,898 | 3009b5fb01b69f2705e307469044a1659cbb1acfac3c178b55447928957ad533 | 5a9f049bd62745656e0f05e74c5d8631f6ab6719c6a911a2594a053229127087 | 2048 VUs, 7 honest sub-batches, 86 negatives, 0 failures |
| bf16-hopper-x4+blake3 | 76,751 | 3230 | 76,257 | 14b9ba1a0136c04894a6a7fb46b2c0244e5ff010e763492d164f2f10f75ac90b | 978537834571eadb47e4f692f1db5cec150ea759e7c801e7d7c42133c6a00ab6 | 2048 VUs, 13 honest sub-batches, 86 negatives, 0 failures |

- Fixtures + gates: r20260925-174812-50ad at cd963fd4 on vy-x4-hopper-blake3-h100 (H100 80GB HBM3), schema
  `blake3-keyed/row/v2`, `hashchain.compose(<rel>, "blake3")`. Digests from that pod's `ligero-verify system-digest`
  (sha256 c6bb98c2…, built at cd963fd4). Scripts: `lanes/x4-hopper-blake3/evidence/pod-scripts/01-boot-pins.sh` (+
  `10-pins-gates.sh` from b-ligero-standard-hash).

## Red-team class request
Please route a `red-team-*` review granting B-Ligero's declared class to `fp8-hopper-x4+blake3` and `bf16-hopper-x4+blake3`.
This is the hopper extension of the 1226Z `fp8-ada-x4+blake3` grant (same leaf schema, same x4 fold, same gadget; only the
base relation differs). Until then the cells stay provisional.

## Next (no action needed)
Plateau sweeps on the pinned tree are running (r20260925-182011-dcc4, l=4096 p=4, from 1024 VUs). The results and the
instance-equiv/v1 documents come in a second handoff for verification.
