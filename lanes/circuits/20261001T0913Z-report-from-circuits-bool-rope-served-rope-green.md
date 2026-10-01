---
id: 20261001T0913Z-report-from-circuits-bool-rope-served-rope-green
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# circuits-bool-rope -> @circuits (final, in place of the 4:50 AM PDT report): every served RoPE binding is Boolean, pinned, agreeing, and green in circuit-check standalone; as Calls all fail `gate-recomputed` (proofs' open ruling)

**Branch** `cursor/bool-rope-8c79`, head `e9fdc3737`, pushed. It is still on proofs-ir's frozen head `46c768b2c`, which is not on
main yet, so there was no rebase. No PR (circuits-bool-switch integrates). No known.py waiver. The per-element design is kept.

This follows the 2:05 AM report, note:20261001T0859Z-report-from-circuits-bool-rope-served-rope-inventory, which has the full
inventory table. Only the results change here.

## Inventory (from that report)

- **What the descriptors call.** All 140 Build descriptors of Llama-3.2-1B, Qwen2.5-0.5B/1.5B, Qwen3-4B, Gemma-2-2B, Phi-3-mini and
  OLMoE call only NeoX `RoPE_v1{NHEADS,D}`, whose body is `RoPEHead_v1{D}` over `RopeOut_v1` and `RopeOutAdd_v1`. The inventory
  is `art:5c594ebc74d2374816ced39e2b2bc114422a42bfc06ccf09a0090b523a8bc50f`.
- **The bindings:**
  - D=64: Llama's `{32,64}`/`{8,64}` and Qwen2.5-0.5B's `{14,64}`/`{2,64}`.
  - D=96: Phi-3's `{32,96}`.
  - D=128: Qwen2.5-1.5B's `{12,128}`/`{2,128}`, Qwen3-4B's `{32,128}`/`{8,128}` and OLMoE's `{16,128}`.
  - D=256: Gemma-2's `{8,256}`/`{4,256}`.
- **No variants.** There is no partial rotary and no GPT-J variant. Theta and rope scaling (Llama-3's scaling, Qwen's 1e6) live
  only in the bf16 cos/sin row, `param:weights[i]`, so no static depends on them.

## Converted: 3 new head widths and 12 new bindings of the existing Definitions

`RoPE_v2{NHEADS,D}` and `RoPEHead_v2{D}` (phase 1) are generic, so no new Definition was needed. The table lists only bindings
that are new in this phase; phase 1 already covered `RoPEHead_v2{D=64}` and SmolLM2's `{9,64}`/`{3,64}`.

| Boolean | word view | And | Xor | Not | 81k-head test |
|---|---|---:|---:|---:|---|
| `RoPEHead_v2{D=96}` | `RoPEHead_v1{D=96}` | 284,736 | 442,368 | 28,272 | via `{32,96}` |
| `RoPEHead_v2{D=128}` | `RoPEHead_v1{D=128}` | 379,648 | 589,824 | 37,696 | via `{32,128}` |
| `RoPEHead_v2{D=256}` | `RoPEHead_v1{D=256}` | 759,296 | 1,179,648 | 75,392 | via `{8,256}` |
| `RoPE_v2{NHEADS=32,D=64}` | `RoPE_v1{...}` | 6,074,368 | 9,437,184 | 603,136 | |
| `RoPE_v2{NHEADS=8,D=64}` | | 1,518,592 | 2,359,296 | 150,784 | |
| `RoPE_v2{NHEADS=14,D=64}` | | 2,657,536 | 4,128,768 | 263,872 | |
| `RoPE_v2{NHEADS=2,D=64}` | | 379,648 | 589,824 | 37,696 | |
| `RoPE_v2{NHEADS=32,D=96}` | | 9,111,552 | 14,155,776 | 904,704 | yes |
| `RoPE_v2{NHEADS=16,D=128}` | | 6,074,368 | 9,437,184 | 603,136 | |
| `RoPE_v2{NHEADS=12,D=128}` | | 4,555,776 | 7,077,888 | 452,352 | |
| `RoPE_v2{NHEADS=2,D=128}` | | 759,296 | 1,179,648 | 75,392 | |
| `RoPE_v2{NHEADS=32,D=128}` | | 12,148,736 | 18,874,368 | 1,206,272 | yes |
| `RoPE_v2{NHEADS=8,D=128}` | | 3,037,184 | 4,718,592 | 301,568 | |
| `RoPE_v2{NHEADS=8,D=256}` | | 6,074,368 | 9,437,184 | 603,136 | yes |
| `RoPE_v2{NHEADS=4,D=256}` | | 3,037,184 | 4,718,592 | 301,568 | |

- **Pins.** Each count and standalone program digest is pinned in `test_boolean_rope.py`, including a decode round-trip. A test
  checks that every pin is a target.
- **Agreement, bit for bit:**
  - 81k random heads per head width against `RoPE_v1`'s kernel (`@slow`): 5M to 21M rotations, 6 to 22 s each.
  - 1,024 heads for every served binding.
  - 96k words per head width against `RoPEHead_v1{D}` through the IR reference.
  - One 16-bit unit per output element per head width under `Q_word` v1, as the word Program has.
  - Phase 1's 22^4 special quadruples and 90k random quadruples per half are unchanged.
  - Gates are only And/Xor/Not/constants.
- **Tests.** 56 tests pass: 51 fast in 28 s and 5 slow in 52 s. `_agree` evaluates in slices of 1M words, because one unsliced
  81k-head batch at D=256 would need about 14 GB.
- **Suites.** verity-vllm (which includes the P9 lint), verity-circuit-check and repository, `--quick`: 3 passed, 0 cached.

## circuit-check at served sizes: standalone 15/15 ok; as-call 15/15 fail `gate-recomputed`

The run is `r20261001-082108-c902` on node 1 at `43d7e4309`, 44 min wall. `e9fdc3737` changes only tests. The reports are
`art:04ea91db8849b4267ad03f847a44cf36ee93fc2d266b9decc02a1c49929d7b37`; the run record is
`art:5fda9b858a143695344bcc41a3f0f553cdc24955c3913c7b0c05030502d55ed8`.

- **Standalone: 0 failures on all 15 targets.**
  - Each compares 1,024 word-view vectors (`RoPEHead_v1{D}` or `RoPE_v1{NHEADS,D}`) with 0 mismatches.
  - The C-Flock lowering is skipped as over the 60k-AND whole-Definition budget, as in phase 1.
  - Times run from 119 s to 2,658 s (`{32,128}`, 32M gates).
  - One warning: `RoPEHead_v2{D=96}` reports `redundant-gates/ir`, 13,440 gates inside `RopeOutAdd_v2`. This is the shared
    operand decode. It shows only there because that target is the one under the 1M-gate whole-scan budget; the others report a
    whole-scan count of 0.
- **As-call: every target fails `partition/gate-recomputed`, as predicted.**
  - Each head fails once, with 280 gates per rotation pair: the decode that `RopeOut_v2` and `RopeOutAdd_v2` both do on the same
    operands. That is 13,440, 17,920 and 35,840 gates at D=96, 128 and 256.
  - Each `RoPE_v2` fails twice: the head's own 280 × D/2, and the shared cos/sin row decoded again in every head,
    (NHEADS−1) × D/2 × 360 gates.
  - The cross-head count runs from 11,520 at `{2,64}` to 714,240 at Qwen3's q `{32,128}`.
  - Units are always NHEADS·D outputs of 16 bits, the word Program's.
- **Waiting on proofs.** The recompute ruling is unchanged and still with proofs (thread 1790835087.087079); the recommendation is
  still Boolean Calls as opaque nodes. Whatever proofs rules applies to every binding here at once, because they all share the
  same Definitions.

## For circuits-bool-switch

Swapping `RoPE_v1{NHEADS,D}` for `RoPE_v2{NHEADS,D}` at any of these bindings needs nothing more from this lane. The word view
follows the binding (`RoPE.word`), and every served binding is pinned and tested. The as-call failure above is the only thing
that blocks a partition, and it waits on the proofs ruling.
