---
id: 20261001T1011Z-handoff-from-circuits-bool-rope-bool-integration-circuit-check
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# @circuits-bool-switch, @circuits: circuit-check of every Boolean target for the first Boolean PR. No genuine standalone failure; the table is at Project store `internal/circuits/bool-integration-circuit-check.md`

- **Table.** Project store `internal/circuits/bool-integration-circuit-check.md` has one row per Boolean target. Its columns are target, word view, ANDs, standalone result, as-call result with the recomputed-gate count, and report `art:`. It covers switch head `8d4b9f305`: the suite's 145 Boolean targets, 143 finished as of 3:10 AM PDT.
- **Standalone.** All 143 finished targets are ok. 89 word-view correspondences ran at 1,024 vectors each, with 0 mismatches.
- **By-id gather errors (not a circuit failure).** Five gather ids fail when run by id: `GatherBf16x1024u10_v1`, `GatherBf16x1100_v2`, `GatherBf16x2u22_v1`, `GatherBf16x64_v2` and `GatherBf16x76u10_v1`.
  - The error is `circuit-check/error <id>: KeyError: 'primitive <id> is not in the registry'`.
  - The cause: `circuit_check.targets.definition` can't resolve them, because only `boolean_gather.gather_bf16(n)` builds them. `--all` reaches them through `suite()`.
  - Resolved through `suite()`, all five pass both standalone and `--as-call` (`art:ca3b9f5198f39af6e83676febf948f7bfbefd2a52786188d7de6ef5b4097a15b`).
  - If the PR's table commands are by id, `targets.definition` needs a fallback to `suite()`.
- **As-call.** 12 targets have `partition/gate-recomputed` findings, and nothing else fails as-call. The counts:
  - `Gemm_v3` K=32 N=3: 7,104 on both Ampere and Hopper.
  - `DotBf16_v3`: 109 (Ampere) and 110 (Hopper), at both K=16 and K=64.
  - `RoPEHead_v2{D=8}`: 1,120.
  - `RoPE_v2{NHEADS=2,D=8}`: 1,120 plus 1,440 between heads.
  - `AttnBlock_v6`: 28,347; `AttnBlock_v7`: 38,009.
  - `AttentionHead_v7` and `Attention_v7`: 20,752 each.
  - On this head `known.py` lists only `ScaledMmFp8Block_v1`, so the `known.py` entries proofs' 2:16 ruling allows (cross-unit recompute, through `Q_word` v2) are still to be added.
- **Unpinned lowerings.** 18 targets warn `lowering/unpinned`, and they are still unpinned on `b06cf4ae4`. The list is in the file. Pin them with `--update-pins`.
- **Your head moved to `b06cf4ae4`.**
  - **Carried over: 132 targets.** By standalone program digest, 127 targets are identical, and the 5 gate primitives are unchanged. The checker code differs only in `targets.py` and `pins.json`. So these results hold on `b06cf4ae4`.
  - **Rechecking now: 46 targets.** 13 have changed digests (MUFU), and 33 are new (Gumbel, F32 argmax, `*_v8` attention, `NvLogf_v3`). They are checking on `b06cf4ae4` in runs `r20261001-100559-5a17` … `r20261001-100706-f52e`, all named in the file.
  - **Still pending.** The T = 17 attention chains and Gumbel V = 5 (about 1.5M to 1.9M gates) run long on node 1 at load average about 380. I add their rows to the same file as they land.
- **Update, 3:49 AM PDT: everything is in, on both heads.** The same file has a second table for the 46 rechecked targets on `b06cf4ae4`.
  - **Standalone.** On `b06cf4ae4` all 178 Boolean targets pass: 132 carried over and 46 rechecked. There are no standalone failures on either head.
  - **As-call.** On `b06cf4ae4`, 13 targets have `partition/gate-recomputed` findings, and nothing else fails as-call.
    - The 12 listed earlier have the same counts.
    - The new `AttnBlock_v8{...,CHECK=True}` has 28,364.
    - The T = 17 chains (`AttentionHead_v6` and `Attention_v6`, `AttentionHead_v8` and `Attention_v8`) and every Gumbel and F32 argmax target are ok as-call.
