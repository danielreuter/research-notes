---
lane: lean-gemm-relation
kind: handoff
from: lean-zk-table
created: 2026-09-30T10:07Z
---

# lean-zk-table: two more §4 rows, and one record changed (supersedes the 09:32Z rows' records)

#519's head is now `070b209d`, with 11 new pins. The 09:32Z rows stand, with these changes.

**Changed record:** `ZK.padsOnto_monomial` is now `d97bd15d`. The statement is the same, minus three unused instance
arguments.

**New rows**, after the `ideal_leaf_swap` row:

| Theorem | What it says | Status | Assumptions | Record |
|---|---|---|---|---|
| `FlockSoundness.ZK.ideal_leaves_swap` | T1 over `n` leaves (the hybrid): swapping `n` real hm96 leaves for ideal ones changes any event's probability by at most `n·δ₁` | proved, pinned in [#519](https://github.com/danielreuter/verity/pull/519) | **`Hm96Hiding`** | soundness, `308290c1` |
| `FlockSoundness.ZK.Table.table_shvzk_hm96` | **Lemma B with real leaves**: under `table_shvzk`'s hypotheses, every event on the view has probabilities within `2·N_hid·δ₁` of each other under the real prover (hidden leaves real hm96 leaves of what they commit) and under `S_shvzk` with real leaves | proved, pinned in #519 | **`Hm96Hiding`** (HDK); the `Hm96` structure (a leaf is `H(dig + M·y, c(y))`); `table_shvzk`'s hypotheses, `InnerHolds` included | soundness, `2a1fddd7` |

**The gap line becomes:** Lemma B (SHVZK, with its `2·δ₁·N_hid` bound) is fully in Lean. The Goldreich–Kahan hybrids, Lemma C's adaptive lift, T6's extraction and T7's generating function stay on paper. The clear protocol's completeness, and so `InnerHolds`, is not in Lean.

**The recorded audit** of `070b209d` is `r20260930-100629-d228`. It is still running; I'll label it when it's done.
