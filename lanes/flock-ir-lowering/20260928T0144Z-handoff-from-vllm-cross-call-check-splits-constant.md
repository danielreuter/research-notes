---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-ir-lowering (bc-9916bbb1) · kind: handoff · from: vllm-cross-call-check · cc: research coordinator (bc-8ece7cde) · created: 2026-09-28T01:44Z · re: your 19:35Z splits-anchor handoff, proposal 1

# `splits` is a constant in single-request Programs: PR #197, #101 is now `79caee21…`

Daniel approved proposal 1 at 00:25Z. It's up as [#197](https://github.com/danielreuter/verity/pull/197) on `main` `df3bc5e1`. It is a statement change, so red-team-flock-3 reviews it before it merges; after that it joins the overnight queue behind M0's prover PR (#192).

**What your side sees.**
- **Inputs.** A single-request request Program's inputs are `prompt, seed`; there is no `splits` input.
- **The 6th operand.** Every `GumbelTopPTokenSelect_v1{V=128256}`'s 6th operand reads a `Const32[0x00000020]_v1` call. The call is named `<select node>/splits` and is emitted right after the temperature literal. Nothing else reads it.
- **S.** S = `SplitsFor_v1(1, num_SMs)` from the target's SM count: 32 on L40S (142 SMs) and H100 (132).
- **Multi-request workloads** keep the `splits` input.
- **Program size.** Gates are unchanged at 20049835919: the keep word is not specialised yet.

**#101 Build** (L40S pod, the target read from the device as the record did; both runs preserved on R2):

| | base `df3bc5e1` (reproduces the record) | #197 |
|---|---|---|
| run | `r20260928-012525-4b0f` | `r20260928-012534-6768` |
| program digest | `ccc213475e7c4eed…` | `79caee21b124d591fe9bc003142660e071aacc443e4a6fdba16a1a6581e4684c` |
| required-value manifest | `90f81868…` | `eb393312c2c39592…` (the 32 `sampler_splits` identities go) |
| program graph (instances only) | `a2c23989…` | `9fbbb557…` (+32 literal groups, one per select, +1 Definition) |

`research fetch r20260928-012534-6768 --all`, then `out/build_request/` has `descriptor.json.gz` and `instances.json.gz`; `out/program_graph.json` is the graph.

**The keep-word side is yours**, as you proposed:
- specialise #125's `TopPMaskWordx128256_v1` (or its lowering) when S is a literal, keeping only the pipeline S selects;
- your estimate was ~1.45e11 → ~2.4e10 ANDs per step, about −3.9e12 on #101;
- the anchor itself needs nothing further from the lowering: the constant is in the Program.

Tell me if you want #101's boolean-circuits export regenerated from the new Build, or anything else from the vLLM side.
