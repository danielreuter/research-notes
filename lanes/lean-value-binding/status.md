---
cursor:
  subagentId: "bc-a84aadb3-b06e-5db9-b0e4-e63614938d81"
---

# lean-value-binding: status

Agent bc-a84aadb3 (lane `lean-value-binding`, brief `internal/lane-briefs/lean-value-binding.md`). Newest first.

- **07:45Z** soundness building in my own tree on vy-nebius-1 (`/workspace/research/trees/lean-value-binding`, deps copied
  from the warm `lean-deps` cache, CPUs 0-31, the unpinned pool of the 07:13Z map). Design for the binding settled: `Val` a
  row, `Com` the leaf digest `SHA-512(leaf_prefix ‖ b ‖ c)`, `collide` an explicit three-way extractor (outer, salt, row
  hash), reusing `Merkle.hm96Leaf` and `Refine.K512`/`H512`.
- **07:35Z** started. Plan: (1) PR pinning the five knowledge-soundness theorems (`table_knowledge_sound`,
  `table_knowledge_sound_joint_tight`, `session_knowledge_sound`, `flock_batched_knowledgeSoundE`,
  `flock_batched_linkSoundE`), branch `cursor/lean-knowledge-pins-8d81`; (2) `FlockSoundness/Binding/` building
  `Partition.ValueBinding` from HM96 rows, `registered_weights`, and the e2e restatement, branch
  `cursor/lean-value-binding-8d81`. Recorded audits through `research run --on vy-nebius-1`.
