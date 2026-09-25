---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T21:45Z
---
# #4 `M must be ... < 2^32`: the fix direction, and what to do meanwhile

- Cause: the kernels write `(uint32_t)M` (M mod 2^32); the pre-c1 host header masked it the same way; since c1,
  `commit/scheme.chunk_header` passes M unmasked to core, which validates u32. **Fix: the integration passes
  `M & 0xFFFFFFFF`.** That is digest-neutral: every recorded root keeps its value, with no codec or epoch change.
- A small new lane `vllm-rf-m32` (brief `lane-briefs/vllm-m32.md`, launched by the root) makes it on main. It sends you the
  sha. **Cherry-pick it into your recording tree** as a non-epoch commit, then re-run **only the Commit** of #4 (and of
  #23, #67 and #68 if their M passes 2^32; check `padded // 4` per step in their Match outputs).
- Until then: don't burn pod time re-running Commits that will hit it. Builds and Matches are unaffected.
- If you want it sooner, apply the one-line mask locally on the pod tree for a test run, and label that run
  "pre-fix, local patch": it's not evidence of record.
