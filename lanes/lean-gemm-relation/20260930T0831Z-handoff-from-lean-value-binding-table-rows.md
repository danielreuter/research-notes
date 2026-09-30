---
lane: lean-gemm-relation
kind: handoff
from: lean-value-binding
created: 2026-09-30T08:31Z
---

# lean-value-binding: rows for the security theorem table (`theorems.md` §1 and §3)

For `internal/lanes/lean-gemm-relation/theorems.md`, which is yours. Replace the "not pinned" and "to write" rows of §1 with
these, and add the §3 row. Records are the first 8 hex digits of `type_hash` in `soundness/lean-audit.json` on the PR heads.
Both PRs await red-team-flock-3's statement grant.

**§1, replacing the knowledge row and `registered_weights`:**

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.table_knowledge_sound`, `…_joint`, `…_joint_tight`, `session_knowledge_sound`, `Audit.Partition.flock_batched_knowledgeSoundE` | Knowledge soundness: extraction fails with probability ≤ ε_c⁻ + K·Adv₀ + N₀/(eK) (tail form: that over ε − ε_c⁻) | proved, pinned in [#511](https://github.com/danielreuter/verity/pull/511) | explicit collision-finder terms, as compiled | soundness (#511) |
| `Audit.Partition.flock_batched_linkSoundE` | The link theorem: δ_link ≤ Q_s/(1−ρ)·(2t'(1+k)/2^256 + 1/(eM) + k/(eR_w)) | proved, pinned in #511 | **A2** for each commit string's finder; `ValueBinding` (named) | soundness (#511) |
| `FlockSoundness.Binding.Layout.registered_weights`, `HmRows.registered_weights_hm96`, `registered_weights_extracted` | The row a satisfying (or extracted) witness holds at a drawn unit's wire is the registered one, or `collide` is an explicit SHA-512 collision (outer hash, salt digest or row digests) | proved, pinned in [#513](https://github.com/danielreuter/verity/pull/513), 0 sorry | none cryptographic: the conclusion is a collision. Hypotheses: **`HmRowComputes`** (the circuit's row hashing, phase 2i; `Assumptions`), the layout's facts (`Layout.decode_row`, `HmRows.bc_registered`, `other_registered`) | soundness (#513) |
| `FlockSoundness.Binding.hm96Pair_spec`, `Layout.collide_spec`, `HmRows.registered`, `hm96_treeLeaf` | hm96's explicit extractor outputs a SHA-512 collision; the binding's `collide_spec`; the registration fact from `HmRowComputes`; the model's leaf is the executable's `treeLeaf ∘ commitString` | proved, pinned in #513 | none (`registered`: `HmRowComputes` and the layout's facts) | soundness (#513) |

**§3, a new row after `flock_e2e_drawn_exec`/`_count_exec`:**

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.Binding.flock_e2e_count_hm96`, `_drawn_hm96`, `_count_exec_hm96`, `_drawn_exec_hm96` | The end-to-end bounds with `vb` built from the serving rows (`HmRows.binding`) and the link finders' hash SHA-512 itself (`H512`) | proved, pinned in #513 | **A2** (`hCR`, for SHA-512); **`HmRowComputes`**; the layout's facts; the skeleton's `hExec`, `dp`, `hL1`, `hOne` (unchanged) | soundness (#513) |

Gap line for the morning report: `ValueBinding` is no longer a bare hypothesis. What's left of it is one circuit fact,
`HmRowComputes` (phase 2i), and three layout facts, each with an owner in `assumptions/e2e-checklist.md`.
