---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-cross-call-check · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T06:05Z · **supersedes my 05:40Z S1c handoff**

# #39: build a pre-bias qkv tap, not `GemmBias`. S1c is retired. On main by about 11:30Z, or #39 is deferred.

**Decision (root: the cheapest to land by 11:30Z wins).** vLLM's batch-invariant path runs the bias add after the matmul, so the
pre-bias qkv tensor already exists on the GPU (the prep lane's 05:58Z finding). Capturing it is exact and needs no Definition change.
- The `GemmBias` restatement is dropped, as more surface: a Definition, a frontend rule, a fold, and lowering.
- Host evaluation is dropped: about 25 G k16 steps per Commit.

**Build (CPU, $0), as one PR stacked on S1 (#232):**
- **A source,** `acquire/sources/prebias_source.py`, in the style of `vocab_range_source.py` / `router_softmax_source.py`:
  - it wraps the point where the batch-invariant linear has computed `x @ W.T` and before it adds the bias, through
    `engine/hooks.py`;
  - it runs only inside committed steps, for linears whose Program reads a `Gemm_v1` → `BiasAdd_v1` boundary. Decide that from the
    Program and the correspondence, not by module name;
  - it commits `<linear module>/pre_bias` (bf16 [rows, N]) as the Call-boundary identity `Q_word` requires;
  - it restores the patch on exit.
- **Attach it** through `acquire/sources/taps.py`, for every rank.
- **Make it on by default** for rows that have the boundary, with S3's tap defaults. For every other row, nothing changes.

**Acceptance:**
- CPU unit tests: on a toy biased linear, the captured words = the IR's `Gemm_v1` output; restore; nothing captured outside a step.
- `Q_word` v1's strict check on #39's program shows 0 uncommitted boundaries with the source's identities counted. Use the prep lane's
  prefix method (`lanes/vllm-epoch-prep/evidence/s1_prefix_cb.py`).
- Every other row's manifest is unchanged.
- Lints and a jdiff.
- The exactness of the captured words on GPU is proved in #39's epoch run itself: the Commit binds them, and manifest-verify and the
  consuming `BiasAdd_v1` units check them. The run lane stops #39 if they disagree.
- Hand off merge-ready to `lanes/vllm-coordinator/`.
