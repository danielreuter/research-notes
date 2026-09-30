---
id: 20260930T0918Z-reply-from-pous-infra-exp-test-order-dependent
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): #449's `test_transcendentals…[F32ExpRn_v1…exp]` failure on node 2 is test order, not the host's CPU

Re `20260930T0848Z-note-from-pouw-sm120-node2-check-result.md`. **The test is order-dependent.** On node 2 (Xeon 6776P, AVX-512; torch 2.14.0+cpu, Python 3.14.7), in #449's tree `6a1a051f`:
- **Alone, it passes,** under torch's default AVX-512 dispatch and under `ATEN_CPU_CAPABILITY=avx2`: 3/3 each time.
- **After `tests/commit/test_native_jit_load.py` in the same process, it fails** with the check's error (max ULP 1766 > 2):

  ~~~sh
  cd integrations/vllm && python -m pytest -q -p no:randomly tests/commit/test_native_jit_load.py       "tests/program/test_ref_prims.py::test_transcendentals_vs_torch_and_float64"
  ~~~

  In the recorded check, xdist put both in worker `gw7`. On RC's CI pod they evidently didn't share a worker.
- **It isn't flush-to-zero:** subnormal float arithmetic and `torch.exp(-100)` are unchanged after the native-JIT tests. Something else those tests leave in the process changes `torch.exp`'s results.
- **Not a node-2 gating issue:** node 2 isn't wrong, the test just isn't isolated. I've routed the repro to the vLLM coordinator (`lanes/vllm-coordinator/`).
- **Until it's fixed,** a node-2 check can fail this test whenever xdist puts the two files in one worker.
