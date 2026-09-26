---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-m32 (bc-7039be6c-2a9f-5501-af51-ee96bf96b428)
created: 2026-09-26T14:05Z
---
# MERGE-READY PR #77: `lane/vllm-rf-bounded-finalize` 7438b2a5 (base origin/main c20bab70): #74 bounded-staging finalize crash

PR: https://github.com/danielreuter/verity/pull/77 (draft). Please forward it to the research coordinator.

**The bug:**
- `--bounded-staging`'s warm-up is a learn-only pass. A learning step over the transient budget commits a placeholder root `b""`.
- `native_host.finalize` folded those roots through core, which accepts 32-byte digests only since c1. It raised `InvalidArtifact: leaf
  must be a 32-byte digest` at the warm-up's finalize (r20260926-115930-46a1), before any record run.

**The fix (`a15bddd7`, line-neutral):**
- `finalize` folds only when every step root is a 32-byte digest, and otherwise returns run root `b""`.
- The warm-up's run root is unused. A record-run placeholder only comes from a worker error, which is already recorded.
- Digest-neutral: runs with all roots fold exactly as before.
- Test `tests/commit/test_placeholder_steps.py` reproduces the exact InvalidArtifact without the fix.

**Admission check for #74 (`a61be4ba`, `7438b2a5`):** raw 152,257 MiB (hidden 139,410); resident 92,046 MiB.
- **Unbounded:** 190,321 + 92,046 = 282,367 MiB, refused at 239,372. This is correct: the run held 229,877 MiB when stopped, with the C2
  Programs still to come.
- **Bounded exclude:** the F-dA-15 pool rule ignored the Merkle levels over the excluded leaves (16,058 MiB, against 59,246 MiB pinned in
  the warm-up). It is now kept + raw × 0.25 = 50,911 MiB, so 142,957 MiB, admitted. This figure is record-only; the bounded HOST BOUND
  (162,049) governs.
- **Still under** (documented, not fixed): the unbounded pool is about 6 % below measured (pow2 blocks), and the planner's C2 Programs term
  for Qwen3-4B-FP8 is 30,141 MiB against the Commit's own forecast of 70,439.

**Gates** (git clone, `verity_sampled_proofs` importable, CPU-only, both runs PRESERVED; evidence scripts `evidence/bf_gate*.sh`):
- r20260926-133406-4d7c (a61be4ba against c20bab70): tests/commit + admission tests, head 389 passed / 0 failed, base 386 passed /
  0 failed, 42 skipped on both sides.
- r20260926-140124-74e1 (7438b2a5): lints rc 0 (the P10 +1 line at a61be4ba is fixed), placeholder + admission tests rc 0.
- Not run: a GPU bounded Commit of #74, to show it completes end to end.

**Pod:** vyv-rf-m32-bf (an A5000 host with the GPU hidden; no CPU stock) was terminated at 14:03Z. Spend about $0.15. Lane total about
$9.7.
