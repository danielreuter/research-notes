---
lane: coordinator
kind: handoff
from: hash-commit-2
created: 2026-09-25T10:24Z
---

# hash-commit-2 merge-ready: lane/hash-commit @ 2a92fe61 (1 commit on main 3301c435, merges clean). GPU committer byte-identical on A100 sm_80 and H100 sm_90

- 2a92fe61 is a fix for a problem the H100 test run found. On sm_90, `torch._int_mm` (cuBLASLt INT8, torch 2.6+cu124) only
  accepts row counts that are multiples of 32, so the Poseidon2 torch int8 MDS failed
  (test_hash_gpu.py::test_poseidon2_tree_matches_reference[torch]). The fix pads the rows to 32 on cc >= 9 and is a no-op
  elsewhere. It doesn't touch the frame-v3 / vllm-v1 committer, which needed no change. Tests at 2a92fe61: 348 passed,
  1 skipped on both H100 NVL and A100 80GB (byte-identity + neighbour suites, no -x).
- Portability at bcf75db7 (main's committer): the byte-identity suites pass 98/98 on the A100 and on the H100. A bench-vu run of
  bf16-hopper+blake3 at 4096 VUs gives commit evidence c90e6d0d… and 49 statement files identical on 4090, A100 and H100,
  with either the GPU or the host committer; Rust accepts 49/49.
- Committer times: H100 3.5 ms (host 15.8 s), A100 5.7 ms (host 27.2 s), 4090 4.9-5.2 ms (host 24-25 s).
- The 4090 rerun at bcf75db7 is closed: fp8 GPU 3.9-4.0 ms vs host 11.9-12.3 s. Artifact ids are in the report,
  lanes/hash-commit-2/20260925T0932Z-report-hash-commit-2.md.
- Pods: vy-commit-gpu terminated 10:09Z and the H100 at 10:11Z; the A100 goes as soon as its registration finishes.
