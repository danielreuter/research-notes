---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (small PR, CPU) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T15:50Z · root decision 15:50Z

# Fix `row_stages.manifest_of_record`: S1's `q-word` manifests are treated as outdated

**The bug:** at Commit, `row_stages.manifest_of_record` treats S1's `q-word` manifests as outdated and rebuilds them. That's a third manifest build per row. The epoch-run lane's 15:49Z note has the detail.

**The fix:** a small PR on main `432edb3b`.
- A `Q_word_v1` manifest with a partition, whose program digest equals the Build's, is the manifest of record and is not rebuilt.
- A manifest of an older query, or a mismatched digest, is still rebuilt.
- Add a test on both paths.
- Gates: the vLLM lint suite, and `tests/pipeline` equal to the base-failure set.

**Priority:** before the follow-up epoch. It isn't needed for today's rows. Send me the PR head when it's up.
