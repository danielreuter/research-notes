---
cursor:
  subagentId: "bc-2840854d-2bab-5494-9ec4-56acb28b827a"
---

lane: circuits-commit-phases · kind: checkpoint · to: @circuits · created: 2026-10-01T14:24Z

**The call-boundary plan is live (7:24 AM PDT)** on two new node-1 trees:

- `cursor-grid-boundary-gm-827a` (`1fff7995c`): gm-feed's 237 unsubmitted items now point at it (backup `items.bak-1415Z.json`).
- `cursor-grid-boundary-cov-827a` (`805ca614e`): vllm-epoch-run and circuits-gemma-sampler have handoffs to submit on it.

Rows in flight keep their trees, and the cutter code is byte-equal. Gemma-2 is still held: GEMMA2_9B sits in gm-feed's `skip_roles`, and
`cov-n050-2` and `cov-n051-2` are held in release.py. Both n050-2 and n051-2 were built on coverage-v1, so they gain only if rebuilt on the new cov
tree. Lifting either hold is yours.
