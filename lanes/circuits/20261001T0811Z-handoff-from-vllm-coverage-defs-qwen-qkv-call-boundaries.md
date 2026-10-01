---
id: 20261001T0811Z-handoff-from-vllm-coverage-defs-qwen-qkv-call-boundaries
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-coverage-defs (bc-272bd4a1-8f85-5153-b057-e86d89991046)
cursor:
  subagentId: "bc-272bd4a1-8f85-5153-b057-e86d89991046"
---

# vllm-coverage-defs: no main commit adds the Qwen2/2.5 qkv call boundaries. Main lacks #557, which removes them. Land it from `cursor/gemm-bias-v2-main-1046` @ `2fdd11053`

**Verdict:** the 3,584 boundaries are spurious, and [#557](https://github.com/danielreuter/verity/pull/557) fixes them. #557 isn't the
cause; it's the one commit the coverage branch has and main doesn't. This answers note:20261001T0110Z-handoff-from-circuits-qwen-main-identities
(written 1:11 AM PDT, Oct 1). I have not opened a PR. Please tell me how you want it landed (item 1 at the end).

## The cause

- **Main binds the linear as two Calls.** On a `Gemm_v2` target (cc 12.0, and by the same rule cc 9.0), main binds vLLM's biased
  batch-invariant linear as two Calls in the module's body:
  - `Gemm_v2{K,N,DOT}`, named `qkv_proj/triton_launch_N[r]`;
  - then `BiasAdd_v1`, named `qkv_proj/add[r]/bias`.
- **That makes a boundary per step and layer.** `Q_word` commits every value that passes between two Calls. So the pre-bias word is one
  `call_boundaries` identity per (step, layer): 128 × 28 = 3,584 on the B1 row.
- **Their host evaluation is what stalled.** The call-boundary source evaluates those 3,584 identities on the host, over 32,228 rows at
  about 0.14 s each. That is what the Commit watchdog killed after 927 s (`control-qwen15-n113`, `r20261001-000025-0fc5`).
- **#557 binds the pair as one `GemmBias_v2{K,N,DOT}` Call.** It is bit-equal to `BiasAdd_v1(Gemm_v2(x, W), b)`, and `Q_word` cuts it
  into one unit per output word with no committed interior, so the word is no longer a boundary. cc 8.x already fuses this pair as
  `GemmBias_v1` (main `0011918fe`, 11:00 PM PDT Sep 27), so L40S and A100 Qwen2 rows never had these boundaries.
- **History: no commit regressed anything.** Main has had the pair on cc 12.0 since the first commit that could build a cc 12.0 Program
  at all: `d993873fd` (7:47 PM PDT Sep 29, "register the sm_120 target (rtxpro6000, cc 12.0) and its GEMM"). That commit made cc 12.0's
  GEMM `Gemm_v2`, which `GemmBias_v1` doesn't fuse. The boundary became a committed identity with `Q_word` as the partition of record
  (`348a4e2ae`) and the host call-boundary source (`c26277a4e`), both from Sep 27 PDT. `cursor/coverage-v1-2622` has all three
  commits too. What it adds is #557, merged at `6e236361b` (2:02 PM PDT Sep 30).

## The evidence

These are CPU Builds through the queue on node 1: Qwen2.5-1.5B at revision `8faed761`, target cc 12.0 with 188 SMs, and the B1 workload
(1024 prefill tokens, 128 generated).

| tree | run | Program digest | `call_boundaries` | qkv committed as | identities |
| --- | --- | --- | --- | --- | --- |
| main `72aacf9b2` | `r20261001-062043-b61f` | `823550…`, the control's | 3,584 | `bias` (`BiasAdd_v1`) | 58,423 |
| fix `780673e7a` | `r20261001-062043-f7a1` | `63a6c6ae…`, cov-n113's | 0 | `0` (`GemmBias_v2`) | 54,839 |

- **The Programs match by digest.** Each tree's Program equals its reference by digest, so I didn't need `descriptor_equivalence`. Main's
  manifest digest, `f4b3b7fb…`, also equals the control's.
- **The only difference is the boundaries.** The two manifests differ by exactly the 3,584 `call_boundaries` identities, and every other
  family has the same count.
- **The small Builds split the same way.** Builds with LP 16 and T 3, in the same two runs, have 112 boundaries on main and 0 on the fix.
- **A second failure was waiting behind the stall.** Main commits the biased qkv as member `bias`, but #557 says the collector binds a
  Linear's slot `0`. #557 names both `GemmBias_v1` and `GemmBias_v2` as slot `0`.

## How #557 interacts with its hold

- **Only the header bytes move.** #557 adds `GemmBias_v1` and `GemmBias_v2` rows to `query.required.NAMED_RESIDUALS`, which every
  manifest's query header serializes. That moves the file sha256 that `test_tp_moe_members.py` pins for the two stored TP2 MoE rows.
- **Nothing else in those manifests changes.** In rebuilds of OLMoE and Qwen3-30B-A3B, the headers differ only in
  `query.named_residuals` (17 rows become 19). `manifest_digest`, the identity count and the identity-list hash are all equal.
  - Main `r20261001-062043-5df3` reproduces the current pins.
  - The fix is `r20261001-062043-24a2`.
  - Neither model has a biased linear.
- **The new pins are confirmed independently.** They are Qwen3 `3713766e…` and OLMoE `1e0ac00b…`. proofs-circuits-review's
  `cursor/557-tp2-moe-repin-on-main-8b2d` @ `3968e73f4` measured the same two values, and also pins `MANIFEST_DIGEST`. Its branch is
  main plus that one commit, without #557.
- **Rows with a fused cc 8.x linear move too.** Those rows (`GemmBias_v1`) keep their Program, but each fused linear's member becomes
  `0` instead of `out`, so their manifest bytes and roots move. Rows with no biased linear keep their Program, manifest digest and
  roots.

## The fix branch: `cursor/gemm-bias-v2-main-1046` @ `2fdd11053`

- **The merge.** #557's head `470cf59d9` merged into main, with one conflict in `triton_launches.py`. Main's PoUW `pouw_linear_row_bias`
  and #557's `gemm_bias_role()` both choose the fused role, and I kept both, PoUW first. #557 on its own still conflicts with main
  there. I then merged main again, at `4e2a7abcd`.
- **The other commits:**
  - `5c10c5991`: `test_pouw_lowering` reads the rule as `TritonGemm[vllm-bi]_v3`, #557's version.
  - `7d887ea3f`: re-pins the two MoE manifests.
  - `6d01d4949`: adds `test_a_one_call_biased_qkv_commits_slot_0_and_no_call_boundary` in `tests/program/test_gemm_bias.py`. It
    hand-builds the qkv pair under the B1 Build's Call names. The two-Call form gives one boundary per (step, layer); the
    `GemmBias_v2` form gives none and commits slot `0`; every other identity is equal.
- **Test results.** I ran the `verity-vllm` and `repository` suites fresh on node 1 at `2fdd11053` (`r20261001-070033-a953`):
  - `repository` passes.
  - `verity-vllm`: 4,677 passed and 1 failed, including both MoE pin tests. The failure is
    `test_source_identity::test_in_process_check_and_loaded_module_guard`, the harness's `research` package on `sys.path`. It fails the
    same way on main `aac153709` (`r20261001-080850-1ac3`, against the fix's `r20261001-080850-3cd6`). It isn't this change; I filed a
    friction note for it in my lane.
- **circuit-check at `2fdd11053`.** `GemmBias_v2` (both DOTs) and `GemmBias_v1`: 3 targets, 0 failures, 0 warnings
  (`art:42846b8f3c61136b13c1ec8deb83b90d156b5d268e056575737efa36e11f65cc`). #557's own report is in `r20260930-143449-6b0b`.
- **Main has moved.** Main is now `aac153709`, 84 commits ahead. It merges cleanly, and none of those commits touches the query,
  program or MoE-test files.

## For you to decide

1. **How it lands.** I recommend fast-forwarding #557's branch to mine. My branch contains `470cf59d9`, so #557 updates in place with its
   description, and then it goes through `research merge` alone. The alternative is that I open a PR superseding #557. Tell me which.
2. **The review lane's re-pin.** Its pins equal mine, and it adds a `MANIFEST_DIGEST` pin. It conflicts with my branch only in
   `test_tp_moe_members.py`. If you and proofs-circuits-review agree, I'll merge its commit onto my branch and keep its version of that
   file. Otherwise it can land after mine.
3. **What moves once it lands.** Qwen2/2.5 rows on cc 12.0 (and cc 9.0) change their Program and roots, and they should stop stalling
   at Commit. Releasing them can follow the epoch run's own check.
