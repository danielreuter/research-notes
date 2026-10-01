---
id: 20261001T0728Z-report-from-circuits-bool-switch-switch-and-purity
campaign: verity
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits: the switch and the purity check are on `cursor/bool-switch-8c79` @ `933c5e045`. Purity on SmolLM2: 36 non-Boolean Definitions (744 specializations), 4 gaps (12:29 AM PDT)

## What is on the branch

**The switch.** `TargetProfile.ir = "boolean"` makes the Build take `verity_vllm.program.boolean.derived(report)`. That is the
word derivation's report with its Program on bits: the same Calls in the same order, each of the Boolean version of its
Definition. A Call with no Boolean version is refused by name (`numerics_unregistered`, every missing id listed).

The default derives on words exactly as before:
- `derive.py` is byte-identical to `46c768b2c`.
- `ir` is absent from the profile's JSON, so no profile digest moves.

**The table.** The table is the Boolean Definitions' own `word` links. Two refinements:
- `word_statics` binds a static the word lacks, such as the norms' MUFU statics.
- A bare op name in the frontend resolves only to word Definitions, so registering `AmpereBF16TcDot16_v3` no longer breaks
  frontend tests that depend on test order.

**The purity check.** `verity-vllm boolean-purity DESC [--dry-run] [--out JSON]`.

## Purity count on `cov-k01-10`

The row is SmolLM2-135M TP1 B1 greedy 256/32, Program `6ea7c413…`.

- **The word Program:** 54 non-Boolean Definitions (763 specializations).
- **The dry run at the branch head:** 36 (744).

| Word Call | Calls | Boolean version | Owner |
|---|---|---|---|
| `Attention_v5` | 8,610 | none | proofs-ir-attn |
| `Gemm_v2` | 34,472 | none (Gemm_v3) | proofs-ir |
| `RMSNormFusedCuda_v2` | 17,220 | none (see below) | norms, then proofs-mufu |
| `RMSNormTriton_v1` | 287 | none (see below) | norms, then proofs-mufu |
| `Embedding_v1` | 287 | `Embedding_v2` | casts |
| `RoPE_v1` | 17,220 | `RoPE_v2` | rope |
| `SiluMul_v1` | 8,610 | `SiluMul_v3` | silu |
| `TokenSelect_v1` | 32 | `TokenSelect_v2` | sampling |

## Branches merged

- elementwise `0d2dc46fe`
- rope `50156733c`
- silu `2b2e176f8`
- sampling `f2b9f2a24`
- casts `9992aca83`
- norms `04ffd8cac`
- `cursor/bool-trace-emit-f91f` `715da99a0`: one commit off proofs-ir that gives `trace._body` its public name, `trace.emit`

proofs-ir-attn and proofs-mufu-bool are not on origin yet.

## Not green yet

Each problem has a handoff to its owner, asked for by 4:00 AM PDT.

- **vLLM lint P9** fails on four branches on their own: rope, casts, norms and sampling. Each assigns `X.word = lambda`/def to
  a `@composite` object. Silu's fix, in `2b2e176f8`, is the pattern. The allowlists are ratchets, so I haven't touched them.
- **P1:** norms and sampling read `trace._body`. Both are fixed on the switch branch with `trace.emit` (`933c5e045`).
- **circuit-check** fails on norms: no binding reaches 18 of its Definitions, and the branch has no tests.
- **Sampling's strict xfail** `test_word_view_at_one_logit` XPASSes whenever rope's tests import
  `verity_vllm.program.kernels.twins` earlier in the process, so its result depends on test order.

## Call boundary: norms

The norms' Boolean versions can keep the Call boundary, but only as the whole-norm composite: `RMSNormFusedCuda_v3`, whose word
view is `RMSNormFusedCuda_v2`. At N = 576 that is 7,153,598 gates per Call, or 6,869,682 for Triton, before the MUFU are on
bits. SmolLM2 has 17,220 such Calls.

The owner designed root-level parts instead ("never the whole norm"). Under the hot swap I use the whole Call. Say if you want
otherwise.

Even with `word_statics` set, the norms stay a gap until proofs-mufu publishes `RsqrtApprox_v2` and its siblings. I don't bind
`WordOnBits`, because that would leave word gates in the Program.

## Re-verifying the Commit's 460 units

**The source.** The sealed full replay bundle of this row on node 1, read-only:
`/workspace/jobs/probe-jit/cfgtp2-deferred-smol2/D/sweep/<row>/commit/replay_bundle_p0`. It has run root `a48fbe4e…`,
Program `6ea7c413…` and k = 460.

**The method.**
1. Rebuild the word function from `build_request` and check it against the digest. A prototype matches `6ea7c413…`.
2. Build σ, the map from each word id to its Boolean id, with each entry's circuit-check `word_view` result.
3. Check P' = σ(P) against P node by node.
4. Run replay's draw from the run root and evaluate each pick's Boolean body with `verity.evaluation.bits` on the committed
   inputs.

A pick whose Call has no Boolean version yet is reported, and not evaluated. That allows a partial run now, then all 460 once
purity reaches 0. The job runs as a queued CPU job on vy-nebius-1.

## The PR

I'll open one PR by 5:00 AM PDT with every family that is green by then. Families that aren't stay off it. What is the status
of proofs-ir's IR PR, so I can rebase onto main?
