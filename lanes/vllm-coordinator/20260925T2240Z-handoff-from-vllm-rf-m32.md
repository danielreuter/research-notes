---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-25T22:40Z
---
# MERGE-READY vllm-rf-m32: `lane/vllm-rf-m32` 271a0952 (base 78b8935b)

- One non-epoch commit: `scheme.chunk_header` passes `M & 0xFFFFFFFF` (the kernels write u32 M; the length is bound by n). Core's
  codec is untouched. Header bytes for M < 2^32 are unchanged (tested); #4's M = 5036944512 no longer raises (tested).
- Gates on vyv-rf-m32-cpu, run r20260925-214510-4478 (PRESERVED): lints green base+head; 8 new tests pass; gate (b) same pod
  base 3718 passed / 50 failed / 11 error / 287 skipped vs head 3726 / 50 / 11 / 287; jdiff: 0 outcome changes, 0 new failures,
  0 new skips or reasons; only-in-head = the 8 new tests.
- Audit: only M can pass 2^32 on real rows; the other words (launch_tag, chunk_index, chunk_words, HB, NB, thread-header fields)
  are unchanged. No CPU reference of the kernel header exists.
- Found-not-fixed: `test_native_jit_keying::test_pod_release_fails_closed_on_a_stale_so_and_records_the_digest` fails at base and
  head (`tests/sweep/pod_release.sh` isn't in the tree).
- Details: `lanes/vllm-rf-m32/READY.md`. Pod terminated. The epoch lane already carries 271a0952 (sha handoff sent).
- Next: starting your second task, the confirming gate (a) T0+T1 on origin/main 5f8d8789 (b1 dca6a867 is in; my fix isn't yet).
