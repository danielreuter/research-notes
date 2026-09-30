---
id: 20260930T0918Z-handoff-from-pous-infra-exp-test-order
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> vLLM coordinator: `test_ref_prims.py::test_transcendentals_vs_torch_and_float64[F32ExpRn_v1…]` fails after `test_native_jit_load.py` in the same process

- **Repro,** on vy-nebius-2 (Xeon 6776P, torch 2.14.0+cpu, Python 3.14.7), tree `6a1a051f`:

  ~~~sh
  cd integrations/vllm && python -m pytest -q -p no:randomly tests/commit/test_native_jit_load.py       "tests/program/test_ref_prims.py::test_transcendentals_vs_torch_and_float64"
  ~~~

- **Result:** max ULP 1766 against a bound of 2. The test passes alone, under AVX-512 and AVX2 dispatch alike.
- **Not flush-to-zero:** subnormals and `torch.exp(-100)` are unchanged after the native-JIT tests, so some other process state leaks.
- **Where it showed up:** a recorded check (`r20260930-081604-5569`, xdist worker `gw7`). It passed on the CI pod, where the two files evidently landed in different workers.
