---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T05:32Z · re: `vllm-epoch-prep/20260928T0505Z-handoff-from-vllm-coordinator.md` and the S4 heads-up (#223 / #221)

# Boundary check rerun: #4 and #101 clean too; only #11 and #39 unchecked. S4 will carry the Ampere re-key and fork after #223

**Row check.** Q_word's Call boundaries against the module-body population, with `word.check_query` non-strict. Evidence: notes
`lanes/vllm-epoch-prep/evidence/s1_cb_101_4.json`, `s1_rows_cb.json`, `s1_cb_small*.json`.

| Row | Source | Extra Values | Boundary violations |
|---|---|---:|---|
| #101 | record Build `art:9cb3a4df` (build_request) | 0 | none |
| #4 | record Build `art:8578b716` (LP11_T6) | 0 | none |
| #23, #60 | programs artifacts, smallest shape | 0 | n/a (instances only) |
| #67, #68, #70, #75 | programs artifacts, smallest shape | 0 once the MoE planes count as committed (S1 `4e6ce10f`) | n/a |
| #73 | stored Builds, both FA3 constructions | 0 | none |
| #57, #74 | stored Builds | 62,330 and 21,312 | the chain, and the quant: S1b |
| **#11** | programs `art:db4499e7`: one 0.9 GB Program | **not checked** (VM memory) | same structure as #23 and #101, expected 0 |
| **#39** | programs `art:37cd49bd`: one 1.5 GB Program | **not checked** (VM memory) | expected **affected**: Qwen2.5's biased `qkv_proj` is `Gemm_v1` → `BiasAdd_v1` inside one module |

**#39 and S1b.** The pre-bias Gemm reads only committed values (the norm output and the weights), so option 1 covers it too: the host evaluates
the Gemm. The catch is cost. An exact tensor-core emulation of `qkv_proj` over 4,608 tokens is heavy on the host. I'll measure it
when S1b is up, and propose a restated `GemmBias` Definition only if the host path is too slow.

**S4, per your heads-up.** The Ampere re-key is ready as its own commit: `cursor/epoch-s4-rekey-150d` @ `74b7f51f`.
- It binds core's `AmpereBF16TcDot16_v2`, and deletes the integration's v1 with `_tc_dot16_total` and `_mma`.
- It rebinds the `_v1` string keys in 8 code files. The answer's list missed three places: the `ampere` `dot_id` in `targets.py`, and `vocab.py` / `torch_frontend.py`.
- It also rebinds the test pins and the P11 entry. SP1's `ir_call` gains a v2 mapping, and the numerical bench test now checks that the vLLM step is core's v2.
- It leaves the numerical templates' `_v1` labels alone: they're recorded bench semantics.
- The targeted tests pass; the wide suite is running.

After #223 lands (~06:30Z) I'll fork `cursor/epoch-s4-constructions-150d` from main and fold in S4-A, S4-B and the re-key, resolving `registry/prims.py`. **S4 needs #221 merged first**, because without it C-Flock can't lower a v2 program.
