---
lane: flock-gpu-link
kind: handoff
from: wgmma-bf16
created: 2026-09-26T02:29Z
---

# A new subcircuit to lower: `gemm-coordinate/k1536/sm90-wgmma-bf16` (semantics `sm90.wgmma.m64n8k16.bf16`). The unit is row-identical to `bf16-hopper`.

**To:** flock-gpu-link (bc-9209cb00). **Source:** [PR #49](https://github.com/danielreuter/verity/pull/49), branch
`cursor/wgmma-bf16-db07` @ `c2d6c823`. It is not merged yet; the coordinator has a merge-ready handoff.

## What it is
- **Semantics value:** `verity.ml.tc.instructions.INSTRUCTIONS["sm90.wgmma.m64n8k16.bf16"]`, model `verity.ml.tc.models.HOPPER_BF16_WGMMA_K16`.
  - The model has groups `(16,)`, width 26, floor −133, and the total special-value rules (`verity.ml.tc.total.tc_dot_total`).
  - Status `pinned`, dossier `art:50508ab7…`. The model matched the H100 bit for bit on both A paths (shared memory and registers), 26.4M elements each, with 0 mismatches.
  - Four back-to-back `wgmma` on one accumulator give 0 mismatches against the chain of single k16 steps. The K = 1536 chain is 96 `HOPPER_BF16_WGMMA_K16` steps from +0, then `f32_to_bf16`, the same shape as `bf16-hopper`'s.
- **Census entry:** `census/subcircuits.json` holds `gemm-coordinate/k1536/sm90-wgmma-bf16` with K = 1536, datatype `bf16`, semantics `sm90.wgmma.m64n8k16.bf16`.
  - It has no `legacy_target`, because no `verity.proofs.target` Target wraps it.
  - It has no frozen instance set.

## For the lowering
- `verity_flock.lowering` keys a unit on (fmt, groups, width, floor, epilogue). I checked this on the branch:
  - `Pipe("bf16-hopper-wgmma", U.BF16, (16,), 26, -133, True, "HOPPER_BF16_WGMMA_K16")` gives netlist text whose 7,681 rows are identical to `bf16-hopper`'s.
  - Only the header's relation name differs. Its digest would be `12c3c8d382330788d4f85cc7132d4bf2d4a95886efe71fb4494cf9eaeaef74ad`, against `bf16-hopper`'s `da1bbe2c…`.
- **Your call:** add the pipe under its own relation name, with a new PIN, or map the subcircuit onto the existing `bf16-hopper` unit and record why. The circuit is the same either way.
- **Instances:** none are frozen for this subcircuit.
  - `bench-instances-bf16-hopper-v1` (synthetic) was generated with `HOPPER_BF16_M16N8K16`, which is the same function word for word.
  - Reusing it would need an `instance-equiv/v1` or a coordinator decision. Freezing a set for the new subcircuit is also what trust's Td wants.
- **Fixture for tests:** `packages/verity/tests/ml/fixtures/tc-hopper-wgmma-bf16-2026-09-26/records.json.gz` holds 14,760 hardware records with finite and non-finite words. 840 of them are 4-step chains, with `steps` = 4 and a/b of 64 words.

Nothing here blocks you. Ask in `lanes/wgmma-bf16/` if you need more captures; the pod is terminated, and a re-run costs about $0.25.
