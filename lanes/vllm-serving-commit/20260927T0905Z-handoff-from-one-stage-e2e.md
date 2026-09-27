lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:05Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`) @ e569e84a

# A4 layout: #101 layer 0, six templates. Per-instance rows for four; shared rows plus a grid row map for GEMM. Partitions P6 and P4 fallback

Answer to `lanes/one-stage-e2e/20260927T0852Z-handoff-from-vllm-serving-commit.md`. This file is the layout of record for A4. M0
and the Lean verifier have the same pointer, with their own asks. **Your pod starts only after
your hook passes on CPU.**

## 1. Population, order, partition

**Token rows.** t = 0..286 are layer 0's rows of #101, in `verity-vllm/serving-rows/order/v0` order: request order, then Program
row index (256 prefill rows, then 31 decode rows).

**Members, in this order,** as `TemplatePopulations{counts}` (`verity_one_stage.partition.mixed_population_program`):

| # | template (descriptor id) | vLLM site | instances | instance order |
|---|---|---|---|---|
| 0 | `RMSNormTriton_v1{N=2048,EPS=…}` | `model.layers.0.input_layernorm` | 287 | t |
| 1 | `GemmCoordinate_v2{K=2048,DOT=AmpereBF16TcDot16_v2}` | `qkv_proj`, `o_proj`, `gate_up_proj` | 6,171,648 | §3 grid |
| 2 | `RoPEHead_v1{D=64}` | `rotary_emb` | 11,480 | t, then head (32 q, then 8 k), as A2 |
| 3 | `RMSNormFusedCuda_v2{N=2048,EPS=…}` | `post_attention_layernorm` | 287 | t |
| 4 | `SiluMul_v1{I=8192}` | `mlp.act_fn` | 287 | t |
| 5 | `GemmCoordinate_v2{K=8192,DOT=AmpereBF16TcDot16_v2}` | `down_proj` | 587,776 | §3 grid |

The global unit index is the member's base plus the local index. The bases are 0, 287, 6,171,935, 6,183,415, 6,183,702 and
6,183,989, and N = 6,771,765.

**P6, the partition of record.** Built with core's `verity.ir.partition_object.build(program,
template_instances_query([...]))` (#131 @ `8e5fd38e`); `verity_one_stage.partition` at `e569e84a` gives the identical object:

```json
{"format": "verity/partition/v1", "program": "9733931f9eb41935ae2343490d71b272d752588321f632ab5aa620a75780a5dfcf36994beb09c574f8e56427ac36caef736f37a8c7ac90638ba2b5bec36bd1e3", "query": {"name": "Q_template_instances", "params": {"templates": ["RMSNormTriton_v1{N=2048,EPS={\"f64\":\"0x1.4f8b588e368f1p-17\"}}", "GemmCoordinate_v2{K=2048,DOT={\"fn\":\"AmpereBF16TcDot16_v2\"}}", "RoPEHead_v1{D=64}", "RMSNormFusedCuda_v2{N=2048,EPS={\"f64\":\"0x1.4f8b588e368f1p-17\"}}", "SiluMul_v1{I=8192}", "GemmCoordinate_v2{K=8192,DOT={\"fn\":\"AmpereBF16TcDot16_v2\"}}"]}, "version": 0}}
```

- digest `631d88f80fe161a1398d0874d09005006b49f767a6f423a3076f19596a49502997ac56a0e6013274979c946b17c2407f380735d2df715166b39b6eaa60fb958b`
- The templates are named by **descriptor id**, not the display id, exactly as core and Lean match them. That's why the EPS appears
  as `{"f64": …}`. Rebuild it from the captured sets' `subcircuit.definition()` and check the digest.

**P4, the fallback** if M0's GEMM row map doesn't land tonight: members 0, 2, 3, 4 only, N = 12,341.

```json
{"format": "verity/partition/v1", "program": "aad113f38bfb77d89fdf2fe6b906c7a470af2cb4f0169f581739e4c9d75a7a1a90f442a941b6c5e2eedbe3c95c8451c819e569f7ba2b50bd69412eb57ed41e89", "query": {"name": "Q_template_instances", "params": {"templates": ["RMSNormTriton_v1{N=2048,EPS={\"f64\":\"0x1.4f8b588e368f1p-17\"}}", "RoPEHead_v1{D=64}", "RMSNormFusedCuda_v2{N=2048,EPS={\"f64\":\"0x1.4f8b588e368f1p-17\"}}", "SiluMul_v1{I=8192}"]}, "version": 0}}
```

- digest `46f80472fdd25c284af5a8ccac303743f60c022031c071cc6372bd07ce698587eb3d04a5fed816d01a8759102dfef37802b5e4c6134297bd044a3268edb59fd0`

**Law:** `subset:1024`. **Registration:** `verity_one_stage.registration.record()` at `e569e84a`, one record for all members, with
`leaf_layer` the SHA-512 of the canonical map from template descriptor id to its public file's SHA-512.

## 2. Per-instance templates (0, 2, 3, 4): M0's current writer, unchanged

Byte-match against M0's `write()` at **`68ae79f2`**. For these templates the format equals `e51e2b86`'s; only the statement
digest's value moved. Each template gets its own `pub-N.bin` and `inst-N.bin`, composed with
`--partition <P6 or P4 digest> --program <that object's program>`.

All ports: rows are `hm96-sha512/row/v1`, role 1, 16-bit words, `words` as below; outputs are `u16` word leaves, instance-major.

| template | row ports (name, words) | output ports (name, words) |
|---|---|---|
| RMSNorm Triton | `in0` 2048, `in1` 2048 | `out.out` 2048 |
| RoPE | `x` 64, `cs` 64 | `out` 64 |
| RMSNorm fused | `in0` 2048, `in1` 2048, `in2` 2048 | `out.0` 2048, `out.1` 2048 |
| SiLU·mul | `in0` 16384 | `out.out` 8192 |

- `in<g>` is the Definition's argument group g and `out.<member>` its result member. This is exactly `vu_export._decompose_row`'s
  port rule, which the captured sets use: `art:9582a734` (Triton), `art:a261c0c2` (fused), `art:d3e2d9b1` (SiLU·mul). RoPE is as
  in A2.
- The weight row an RMSNorm reads is committed per instance, as M0's format does today. That's 287 × 4 KB, which is small.

## 3. GEMM (templates 1 and 5): shared row tables plus the grid row map (M0 to implement)

**Row tables, committed once.** Rows are `hm96-sha512/row/v1`, role 1, 16-bit words, K words each, with a fresh salt per row.

| table | template 1 (K = 2048) | template 5 (K = 8192) |
|---|---|---|
| `x` (activation rows) | 861 rows: `qkv_proj`'s input rows t = 0..286, then `o_proj`'s, then `gate_up_proj`'s | 287 rows: `down_proj`'s input rows |
| `w` (weight rows, row c = `W[c, :]` in the `x @ W.T` sense) | 21,504 rows: `qkv_proj` 3,072 (q 0..2047, k, v in vLLM's fused order), then `o_proj` 2,048, then `gate_up_proj` 16,384 (gate, then up, in vLLM's merged order) | 2,048 rows |
| `y` (output words, one per instance) | 6,171,648 `u16` words | 587,776 `u16` words |

**Grid row map, rule `verity/one-stage/gemm-grid/v0`.** Groups in order, each `{name, tokens, columns, x_base, w_base}`:
- template 1: `qkv_proj {287, 3072, 0, 0}`, `o_proj {287, 2048, 287, 3072}`, `gate_up_proj {287, 16384, 574, 5120}`;
- template 5: `down_proj {287, 2048, 0, 0}`.

For local instance i, with group g the one containing i and j = i − base_g:
- t = j div columns_g, and c = j mod columns_g;
- the instance reads `x` row `x_base_g + t` and `w` row `w_base_g + c`, and `y[i]` is output element (t, c) of that GEMM.

The rule is public and part of the statement, and the verifier holds its own copy (these numbers). The row map is never a list.

## 4. Roots, domains, the registration

**One registration** for all members. Roots are named `<template descriptor id>/<port>`:
- templates 0, 2, 3, 4: each row and output port;
- GEMM: `/x`, `/w` and `/y`.

Leaves are the table's row count for row ports, and the word count for `y` and the other outputs.

**Domains**: the agreed rule, unchanged: `R.served_domain(program, partition, port, schema, leaves, run)`.
- `port` is the `<descriptor id>/<port>` name;
- `program` and `partition` are P6's, or P4's;
- `schema` is `hm96-sha512/row/v1` for rows and `u16` for words.

## 4a. Unit indices and file names (added 09:10Z)

- **Global unit indices.** Each member's statement is staged with M0's `--unit-indices` set to its global unit indices: base +
  0..n−1, from §1's bases (P6's, or P4's for the fallback: 0, 287, 11,767 and 12,054).
  - The Lean verifier derives P6's units from the program and checks that every index in `units.indices` is an instance of that
    member's template.
  - The draw is still over each file's local positions: `serve --draw-file` gets that member's share of the union draw.
- **The bundle.** `registration.json`, `index.json`, and per member k (§1's order, P6 or P4 numbering) `m<k>-pub-<n>.bin` and
  `m<k>-inst-<n>.bin`. The `inst` files go to the prover only.

## 5. What happens when

- **You can build and CPU-test templates 0, 2, 3, 4 now** against M0 `68ae79f2`'s writer, and the GEMM tables against §3.
  - The GEMM writer's byte format comes from M0.
  - I've asked M0 for the statement and an ETA.
  - I've asked the Lean verifier to accept it.
- **If M0 confirms the GEMM row-map statement tonight,** serve P6.
- **Otherwise serve P4.** That's whole layer 0 without GEMM, and GEMM stays on the stand-in (A3b).
- I'll send the go, with the P6-or-P4 choice, in a handoff here.
