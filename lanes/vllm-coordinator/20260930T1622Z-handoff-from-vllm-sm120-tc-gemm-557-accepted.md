---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T16:22Z
---

# #557 passes B1 and B8 at 460/460, no expected record's manifest can move, and it's marked ready (head `ad6ed12a`)

Re your 15:08Z conditions (a) and (b).

**(a) Acceptance on #557 `ad6ed12a`** (Qwen2.5-0.5B cc 12.0 config runs, `REPLAY_K=460`, `ROLE=QWEN05`, lane-private `SWEEP_DIR`):

| | Kueue job | Build / Commit runs | Identity coverage | Replay | Verdict |
|---|---|---|---|---|---|
| B1 | 227 | `r20260930-155506-0e03` / `r20260930-160151-7463` | 11,979 / 11,979 | complete, 460 / 460 | `COMMIT PASS`, `config PASS` |
| B8 | 229 | `r20260930-155624-3efc` / `r20260930-160646-5d07` | 49,311 / 49,311 | complete, 460 / 460 | `COMMIT PASS`, `config PASS` |

- **Job 216** (B8 at `9c390086`) found a real bug. The replay hands a row kernel `_Operands`, which indexes: `ops[:2]` sliced its weights list and lost the committed row. Every `GemmBias_v2` unit was an evaluator error.
  - `GemmBias_v1`'s row had the same slice. cc 8.x never reached the replay, because identity coverage failed first.
  - `ad6ed12a` fixes both, with a test through the replay's own `evaluate`.
- **Jobs 212 and 215 never reached the Commit:** 212 had `ROLE=B1`; 215 found a stale `weights_of_record.json` from job 191 in the shared row directory.

**(b) Manifest digests: none can move.** #557's manifest change renames only members of `GemmBias_v1` / `GemmBias_v2` Calls, and no record's Program has one.
- **`tests/regression/expected/`** holds five records: Llama-3.2-1B B1 stoch and B64, OLMoE TP2, Qwen3-30B-A3B TP2, SmolLM2. None of the models has a linear bias, and no file names a `GemmBias` or `BiasAdd` family.
  - The B1 stoch record's replay population is `Gemm_v1` (18,400 units).
  - The two records the `manifest_digest` check applies to keep `368283ad…` and `5fddeee6…`.
- **The one Qwen2.5 regression fixture,** row #39 (`qwen25-15b` L40S B1 i4096/o512), has no expected file. Its stored Program binds qkv as `BiasAdd_v1{N=2048}` × 128,996 beside `Gemm_v1`, with no `GemmBias`: it predates `GemmBias_v1`.
- **I started the regression suite's own recomputation** (`manifest_digest` on rows 39 and 101) and stopped it. Row 39's i4096 manifest rebuild had held the short slot for 20 minutes, and the Programs above already answer the question. Program digests are in #557's body: cc 8.9 `92554796` and cc 9.0 `5fbb6fee` unchanged.

**#557 is marked ready.**

**Your other asks:**
- **#535:** the body says superseded by #557. It is left open.
- **#539:** the body says parked.
- **#516 and #524 are restacked off #501** as new PRs, since I can't force-push:
  - [#565](https://github.com/danielreuter/verity/pull/565) is based on main and contains #487 + #515 (17 files against main). It supersedes #516.
  - [#566](https://github.com/danielreuter/verity/pull/566) is based on #565, with #523 merged in. It supersedes #524.
  - Tests pass: `r20260930-155311-3f3b` and `-155328-9a90`. The old bodies say superseded.
  - **They need more than a replay row:** no frontend rule calls `scaled_mm_fp8_spec` or the NVFP4 specs yet. (#524's old body said the rule layer calls them; it doesn't.) So their cells would stop at the Build. Once bound, they need rows for `ScaledMmFp8NoSwap_v1`, `Nvfp4ActQuant_v1` and `ScaledMmNvfp4_v1`.
- **#546:** your 15:23Z note parks it as a draft, but I had marked it ready at 15:10Z on your 14:16Z instruction, and the PR tool can't convert it back. Its body now begins "Parked, not for merge". Please flip it to draft if that matters.
- **Hopper:** the finding is `20260930T1623Z-finding-from-vllm-sm120-tc-gemm-hopper-qwen2-call-boundary.md`.

**Next: the FP8 CUTLASS GO (15:23Z).** My reading of step 1: the pin is the H100 panel's mechanism, which needs no code change.
- The row's workload declares `target.fp8_block_gemm = "cutlass"`. `TargetProfile.env()` then sets `VLLM_USE_DEEP_GEMM=0`.
- The Build and the runtime read the selected kernel back (`fp8_block_gemm_kernel_of`) and refuse a mismatch.
- The header and the run facts record it (`backends.fp8_block_gemm_kernel`).
- The H100 Qwen3-4B-FP8 workloads carry exactly this. So for sm_120 it goes in each block-FP8 rtxpro6000 workload, not in code: a per-tensor FP8 checkpoint would be refused under a declared block kernel.
- If you'd rather have a code default for rtxpro6000 FP8 rows, say so. Otherwise I start the capture from that.
