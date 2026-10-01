---
id: 20261001T0859Z-report-from-circuits-bool-rope-served-rope-inventory
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# circuits-bool-rope -> @circuits (2:05 AM PDT): the next served Programs call only NeoX `RoPE_v1{NHEADS,D}`, at 12 new bindings; `RoPE_v2` covers all of them, pinned and agreeing; 14 of 15 served-size circuit-checks are green so far

**Branch** `cursor/bool-rope-8c79`, head `e9fdc3737`. It is still on proofs-ir's frozen head `46c768b2c`, which is not on main
yet, so there was no rebase. No new Definition was needed and no known.py waiver was added.

## Inventory: every Build descriptor of the seven models

The source is all 140 coverage rows on node 1, `/workspace/jobs/cov/<cov>/<row>/build_workload/descriptor.json.gz`. Each
descriptor was scanned for every Definition id matching rope, rotary or cos/sin, and every call site with its argument
producers. The inventory, scanner and paths are `art:5c594ebc74d2374816ced39e2b2bc114422a42bfc06ccf09a0090b523a8bc50f`.

| model | rows | RoPE Calls (q, k) | x comes from |
|---|---|---|---|
| Llama-3.2-1B | 29 | `RoPE_v1{NHEADS=32,D=64}`, `{NHEADS=8,D=64}` | `Gemm_v2` |
| Qwen2.5-0.5B | 17 | `{NHEADS=14,D=64}`, `{NHEADS=2,D=64}` | `GemmBias_v2` or `BiasAdd_v1` |
| Qwen2.5-1.5B | 11 | `{NHEADS=12,D=128}`, `{NHEADS=2,D=128}` | `GemmBias_v2` |
| Qwen3-4B | 14 | `{NHEADS=32,D=128}`, `{NHEADS=8,D=128}` | the per-head q/k norm (a concat) |
| Gemma-2-2B | 35 | `{NHEADS=8,D=256}`, `{NHEADS=4,D=256}` | `Gemm_v2` |
| Phi-3-mini | 17 | `{NHEADS=32,D=96}` (32 kv heads: q and k share it) | `Gemm_v2` |
| OLMoE-1B-7B | 17 | `{NHEADS=16,D=128}` (16 kv heads) | `RMSNormTriton_v1` (QK-norm) |

- **One rotation kind.** Every RoPE Call in all 140 descriptors is NeoX `RoPE_v1`. Its body is `RoPEHead_v1{D}`, whose body is
  `RopeOut_v1` and `RopeOutAdd_v1`. There is no GPT-J (interleaved) variant and no other rope or rotary Definition.
- **Full rotary everywhere.** D is the model's head_dim, so there is no partial rotary. Phi-3-mini's 96 is its full head_dim.
- **Theta and scaling live only in the data.** In every row `cs` is a `param:weights[i]` input, the bf16 cos/sin row of the
  token's position. Llama-3's rope scaling, Qwen's theta of 1e6, Gemma's 10k and Phi-3's default are all values of that table,
  not statics, so the circuit is the same for all of them.

## Converted: every served binding, with no new Definition

`RoPE_v2{NHEADS,D}` and `RoPEHead_v2{D}` from phase 1 are generic in NHEADS and D. Their word views
(`RoPE_v1{NHEADS,D}`, `RoPEHead_v1{D}`) follow the binding.

- **Counts.** And = NHEADS·D·2,966, Xor = NHEADS·D·4,608, Not = NHEADS·(D/2)·589. They range from 379,648 ANDs at `{2,64}` to
  12,148,736 at Qwen3's q `{32,128}`.
- **Pins in `test_boolean_rope.py`.** Counts and standalone program digests are pinned for `RoPEHead_v2` at D=96, 128 and 256
  and for all 12 new `RoPE_v2` bindings, beside phase 1's five pins.
- **Agreement, bit for bit:**
  - Each served head width has 81k random heads (`@slow`), compared against `RoPE_v1`'s kernel: D=64 through SmolLM2's q
    and k (phase 1), D=96 through Phi-3's `{32,96}`, D=128 through Qwen3's q `{32,128}` and D=256 through Gemma-2's q
    `{8,256}`. That is 5M to 21M rotations per width, 6 to 22 s each.
  - Every served binding has 1,024 heads.
  - Each head width has 96k words against `RoPEHead_v1{D}` through the IR reference, with no kernel.
  - Each new head width cuts into one 16-bit unit per output element under `Q_word` v1, as the word Program does.
  - Phase 1's special-value grid and 90k quadruples per half are unchanged. Gates are only And/Xor/Not/constants.
- **Results.** 56 tests pass: 51 fast in 28 s and 5 slow in 52 s. `_agree` now evaluates in slices of 1M words, because one
  unsliced 81k-head batch at D=256 would need about 14 GB.
- The affected suites (verity-vllm, verity-circuit-check, repository, `--quick`) are running here.

## circuit-check at served sizes: run `r20261001-082108-c902` on node 1 (from `43d7e4309`; the Definitions are unchanged since)

The run covers the 15 new targets: the three new head widths and the 12 new bindings. Each runs standalone and `--as-call`,
12 jobs at a time.

- **Standalone: 14 of 15 green so far.**
  - Each compares 1,024 word-view vectors.
  - The C-Flock lowering is skipped as over the 60k-AND budget, as in phase 1.
  - Times run from 119 s (`RoPEHead_v2{D=128}`) to 1,326 s (`{32,64}`) on a node at load 140–180.
  - `RoPEHead_v2{D=96}` reports 1 warning; I'll read its kind from the JSON when the run ends.
  - Phi-3's `{32,96}`, at 24M gates, took 1,909 s.
  - Still running: Qwen3's q `{32,128}`, at 32M gates.
- **As-call: 14 of 15 FAIL, as expected.** Each head fails once and each RoPE twice. This is the shared-operand recompute
  (`partition/gate-recomputed`) that is with proofs (thread 1790835087.087079). Per-element design kept; no waiver.

Next: collect the run, confirm the last target, read the warning, finish the suites, and report at 4:50 AM PDT.
