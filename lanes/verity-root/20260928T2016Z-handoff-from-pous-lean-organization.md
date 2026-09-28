---
id: 20260928T2016Z-handoff-from-pous-lean-organization
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: repo-wide Lean organization plan drafted; two findings; one request

Daniel asked for a plan for how Lean is organized repo-wide and what its CI checks. A draft with nine decisions for
Daniel now exists in the POUS Project store (not in the repo). Nothing has been changed in the repo.

**Request.** The plan should supersede or reconcile with your store's `docs/lean-organization.md` (bc-866e1acc,
27 Sep), which we can't read from here. Could you publish it, or a pointer to its decisions, to `lanes/pous/`?

**Two findings that stand regardless of the decisions:**

- **Weak pin hashes.** The audit's pin records use Lean's `Expr.hash`, which is effectively 32 bits (records look like
  `000000003f733f6e`). A lane could change a definition a pinned statement reads while keeping the same record. The
  plan proposes cryptographic, rename-proof content hashes before PoUW lands.
- **Unpinned citations.** The soundness README names theorems it doesn't pin (for example `table_knowledge_sound`,
  `link_sound`), against AGENTS.md's rule that anything cited as proved is pinned.

**The plan in one paragraph.** One Lake package per component beside its code, requiring each other only in Python's
import order (core, then protocols and backends, then integrations); proof-only shared lemmas in
`packages/verity/lean`; cross-area finals in each package's assembly layer (POUS's `PousProofs/Pinned.lean`);
libraries built by glob; research on Verity lane branches, `main` holds prod only; superseded results kept citable by
archive tag, evidence-store artifact and the approach registry; research-notes gets pointers only.
