---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: handoff (merge request) · from: vllm-coordinator · created: 2026-09-30T17:22Z

# Granted and ready for trains: #557, #581, #499

| PR | Head | What | Notes |
|---|---|---|---|
| [#557](https://github.com/danielreuter/verity/pull/557) | `470cf59d91d9567aba7a4cc976c995fc5184866f` | `GemmBias_v2{K,N,DOT}`: the served biased linear (Triton + bf16 bias) on sm_120 and Hopper. Qwen2.5 on sm_120 at B1 and B8 is 460/460. | Clean on main `2e04ac50`. H100 Qwen2 Program digests change; no expected record binds them. |
| [#581](https://github.com/danielreuter/verity/pull/581) | `eec620090eda2de11a63fcf5d55fc5c2bbffcfab` | Dense replay rows (Gemma-2) | Main (TVM) merged in, with the `rows.py` union resolved; tests pass. Per root's order, after #250. |
| [#499](https://github.com/danielreuter/verity/pull/499) | `4b7022986de4cc44e8b3293f3180f97ad95e54f2` | TP2 config run | Your TVL fixes: `%%` in `--replay-k`'s help (Python 3.14 argparse), and the decision test's hidden `.so` in `tmp_path`, not `/workspace/cp`. Clean on main; `test_config_run.py`, `test_tp_world_n.py` and the lints pass. |

- **All three are clean with each other.**
- **Not ready:** #582 (FP8 CUTLASS) carries #515/#516's core and flock parts and conflicts with main and #557. The GEMM lane will send the stack after #557.
- **Parked:** #546 (DeepGEMM quantizer). Don't train it.
