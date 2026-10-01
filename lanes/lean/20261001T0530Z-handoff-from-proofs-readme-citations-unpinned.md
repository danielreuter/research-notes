---
id: 20261001T0530Z-handoff-from-proofs-readme-citations-unpinned
campaign: verity
lane: lean
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# FYI: about 200 unpinned theorem names cited in main's Flock soundness docs; my reading is that the pin rule doesn't reach them

to: lean (bc-19c498a8). From proofs-lean-restate's finish on [#638](https://github.com/danielreuter/verity/pull/638)
(`22fe745f`, 205 pins).

- **What it found:** about 200 theorem names in `main`'s soundness docs that aren't pinned, 159 of them only in the
  README's proof walkthroughs. Four are the ones `ASSUMPTIONS.md` already lists as unpinned.
- **#638 itself is clean:** every theorem the PR body, `ASSUMPTIONS.md`, the README's headline section and
  `e2e-checklist.md` cite as proved is pinned, or the citation was reworded to rest on a pinned one.
- **My reading of AGENTS.md:** "a theorem that a ledger, a table or a PR cites as proved is pinned". A README walkthrough
  that names the lemmas a proof goes through is none of those, so it doesn't need pins. A doc that presents a result as
  established (a status line, a guarantee table, "what is proved") does.
- **No action from proofs** unless you read the rule differently. If you do, say which docs count, and proofs-lean-restate
  pins them or rewords them in a follow-up record.
