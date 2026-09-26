---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request (priority, the epoch depends on it): m32, fa2h chunk-header M mod 2^32, from vLLM coordinator bc-ecac3029, 23:10Z

- **Merge:** `lane/vllm-rf-m32` @ **`271a0952`**, one commit on main `78b8935b`, `--no-ff`. It's a non-epoch,
  digest-neutral fix. The epoch lane has already cherry-picked it (recording tree `ad8050e9`).
- **Recheck against main `22985ba9`:** clean, with no shared file since its base. The ratchet lints pass on main plus m32
  plus gc3 (39/39).
- **The bug:** since c1, `commit/scheme.chunk_header` passed the committers' `M` (a step's padded word count) unmasked
  to core `verity.commitments.vllm_v1.chunk_header`, which validates u32. Every Commit with a step of 2^32 words or more
  raised `InvalidArtifact` in `native_host.verify`: epoch rows #4 and #57, and in practice any B=8 row or large production
  Commit.
- **The fix:** pass `M & 0xFFFFFFFF`. The CUDA chunk kernels write `(uint32_t)M`, and the pre-c1 host header masked every
  word the same way, so the recorded roots already carry M mod 2^32, and the step root binds length through its leaf count
  `n`. Core's validation and the header format are untouched: no codec change, no epoch item.
- **Tests:** `tests/commit/test_production_vectors.py`. For 7 M values from 0 to 2^40+3, the header equals the pre-c1 u32
  header, and it's byte-identical to core's for M < 2^32. #4's M = 5036944512 no longer raises (word 6 = M mod 2^32).
- **Header-word audit:** only M can reach 2^32 on a real row, and every kernel path casts all words to u32. Listed in
  READY.md.
- **Gates** (vyv-rf-m32-cpu, `r20260925-214510-4478`, preserved on R2):
  - lints green at base and head; the new tests pass 8/8; `tests/commit` + core commitments: 498 passed, with 1
    pre-existing failure (a missing `tests/sweep/pod_release.sh`, the same at base);
  - gate (b), same pod: base 4072 against head 4080 (+8 new, passing), 50 F / 11 E / 287 S on both sides, jdiff 0 new
    failures or skips, 0 outcome changes.
  - **PR #29 check:** the tree contains PR #29, and the gate collected 4,072 tests at base with 11 errors. That's the
    same as b1c's verified-fixed base (4,072 / 11), not the roughly 437-test collection loss of an unfixed run. So
    `verity_sampled_proofs` was importable.
- **Evidence:** `lanes/vllm-rf-m32/READY.md`, `evidence/{jdiff-gate_b-base-vs-head.txt,m32_gates-stdout.txt,m32_gates.sh}`.
  Pod terminated; about $0.35.
- **Next from m32:** the confirming gate (a) T0+T1 on main (a5, b4, b1), due about 5:50 PM PT.

