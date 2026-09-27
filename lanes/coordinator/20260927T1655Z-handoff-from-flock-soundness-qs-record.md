---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness · created: 2026-09-27T16:55Z · re: your 16:47Z message (restate the link term of record with `Q_s`)

# The record now counts `Q_s`: a small follow-up, #170, so #163's audited head stays put

[#170](https://github.com/danielreuter/verity/pull/170) is docs only and ready. It is stacked on [#163](https://github.com/danielreuter/verity/pull/163), and #163 is unchanged at `7516258b`, so the merge order is #127, #163, #170.

- **The record** is `t·Q_s(8N₀/e)/2^256.5`, with `Q_s` the expected number of commit strings the drawn units read.
  - Audit B is `t·2^-209.9`, or `2^-129.9` at `t = 2^80`.
  - A, C and D are `t·2^-218.9`, `2^-209.9` and `2^-206.9`.
- **Lifetime at `2^-128`:** `N·t ≤ 2^81.9` for audit B, and `2^78.9` to `2^90.9` over A–D.
- **Files:** `DESIGN.md` §3 and `ASSUMPTIONS.md` (A2's usage, §7's budget) in #170. The strict-time comparison row keeps the earlier analysis's `N_s`.
- **The lifetime doc** (`docs/lifetime-soundness.md`) is restated in the headline, §3, §4, §5 (with the `N·t` table) and §9. §5 now carries the levers table for Daniel, and the sources link #127, #163 and #170. I edited only the body; its frontmatter belongs to bc-1fcbe4c9 and is unchanged.

**Documents.** Created: this note. Updated: `docs/lifetime-soundness.md`, and my lane report (the buy-back section and a checkpoint). No directory changes.
