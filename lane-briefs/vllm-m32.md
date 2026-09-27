---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-m32 (fa2h chunk-header M above 2^32: restore the value of record)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-m32`: a small, digest-neutral fix on main. First read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md` and do its section 1.
> Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md` (it
> overrides the setup page for vLLM lanes, including the no-waiting rule), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-m32.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-m32 open "..."`) within 10 minutes.

## The bug
The epoch lane's row #4 Commit fails in `native_host.verify` with `InvalidArtifact: M must be an integer in
[0, 4294967296), got 5036944512`. #23, #67, #68 and any large production Commit are at risk.

- The `fa2h` chunk-leaf header is sixteen u32 words; word 6 is `M`. For the committers' block layouts
  (`native_host._gpu_layout`) M is the step's padded word count, or 0 under chunk-leaf-v2.
- **The CUDA kernels write `(uint32_t)M`, which is M mod 2^32** (`hidden_gpu_tree.cu:168-170`, `native_tree.cu`
  launch). Before c1, the integration's host header (`hidden_stream.pack_words`) masked every word with `& 0xFFFFFFFF`,
  so the host verify matched the GPU leaves.
- Since c1, `commit/scheme.chunk_header` passes `M` unmasked to core `verity.commitments.vllm_v1.chunk_header`, which
  validates u32 and raises.

## Coordinator's call (don't change the codec)
Every recorded root with M ≥ 2^32 was built with M mod 2^32. Keep that value of record.
- In `integrations/vllm/verity_vllm/commit/scheme.py::chunk_header`, pass `M & 0xFFFFFFFF`, with one comment: the
  kernels write u32 M, and the length is bound by the step root's leaf count `n`.
- Don't touch core's validation, or make M 64-bit. That would be a header-format and epoch change, and it isn't needed.
- Audit the other header words (`launch_tag`, `chunk_index`, `chunk_words`, `HB`, `NB`, the thread header's fields) for
  values that can pass 2^32 on real rows. Apply the same rule only where the kernel also casts to u32, and list what you
  checked.
- Add a test: for a layout with M ≥ 2^32, `scheme.chunk_header` equals the pre-c1 `pack_words` header with the masked M.
  If a CPU reference of the kernel's header exists, test it against that too. Add a second test that #4's shape
  (M = 5036944512) no longer raises.

## Branch, gates and handoff
- Branch `lane/vllm-rf-m32` from `origin/main`. **Bootstrap from `fee32f05` or later**, so `verity_sampled_proofs`
  imports.
- Gates: lints, the new tests, `tests/commit/` and `packages/verity/tests/commitments/`, then gate (b) head against base
  = your main on one cpu3g pod (`vyv-rf-m32-cpu`).
- Digest neutrality: the header bytes for M < 2^32 are unchanged (test), and the #101 path is untouched (its M is small).
  No GPU row is required. The epoch lane re-runs #4 with this commit and reports the Commit result.
- Send a merge-ready handoff to the coordinator as soon as the gates pass, and a second handoff to
  `lanes/vllm-rf-epoch/` with the commit sha, so the epoch lane can cherry-pick it (it's a non-epoch commit).
- Budget: $4. Pod deadline 2026-09-26T03:00Z.

